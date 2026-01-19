import os
import io
import asyncio
import uuid
import httpx
import atexit
from concurrent.futures import ThreadPoolExecutor
from openai import OpenAI
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import fitz
import pytesseract
from PIL import Image
from core.config import Config
from utils.memory import print_memory_usage

class QuestionPaperBot:
    def __init__(self, groq_api_key=Config.GROQ_API_KEY):
        self.api_key = groq_api_key
        self.client = OpenAI(api_key=self.api_key, base_url="https://api.groq.com/openai/v1")
        self.temp_dir = "temp"
        os.makedirs(self.temp_dir, exist_ok=True)
        # Thread pool for CPU-bound OCR operations
        self._executor = ThreadPoolExecutor(max_workers=4)
        # Register cleanup on exit
        atexit.register(self.shutdown)
    
    def shutdown(self):
        """Cleanup resources on shutdown."""
        if self._executor:
            self._executor.shutdown(wait=False)
        # Clean up dummy.pdf if it exists
        dummy_path = os.path.join(self.temp_dir, "dummy.pdf")
        if os.path.exists(dummy_path):
            try:
                os.remove(dummy_path)
            except Exception:
                pass

    async def pdf_to_images(self, pdf_path: str, session_id: str) -> int:
        """Convert PDF pages to images for OCR."""
        print_memory_usage("before pdf_to_images call")
        
        try:
            doc = fitz.open(pdf_path)
            num_pages = len(doc)
            
            for i in range(num_pages):
                page = doc.load_page(i)
                # Higher resolution (300 DPI) for better OCR
                pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
                # Use session_id to prevent collisions between concurrent requests
                path = os.path.join(self.temp_dir, f"{session_id}_Page_{i+1}.jpg")
                pix.save(path)
                print(f"Saved: {path}")
            
            doc.close()
            print_memory_usage("after pdf_to_images call")
            return num_pages
        except Exception as e:
            print(f"Error converting PDF to images: {e}")
            raise

    def _ocr_single_image(self, image_path: str) -> str:
        """Synchronous OCR for a single image - runs in thread pool."""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            image.close()
            return text
        except Exception as e:
            print(f"OCR error for {image_path}: {e}")
            return ""

    async def extract_text(self, num_pages: int, session_id: str) -> str:
        """Extract text from converted images using OCR."""
        print_memory_usage("before extract_text call")
        
        loop = asyncio.get_event_loop()
        tasks = []
        
        for i in range(num_pages):
            path = os.path.join(self.temp_dir, f"{session_id}_Page_{i+1}.jpg")
            # Run OCR in thread pool to avoid blocking async event loop
            task = loop.run_in_executor(self._executor, self._ocr_single_image, path)
            tasks.append(task)
        
        texts = await asyncio.gather(*tasks)
        text = "\n".join(texts)
        
        print_memory_usage("after extract_text call")
        return text

    async def _query_groq(self, prompt: str) -> str:
        """Query Groq API for text generation."""
        payload = {
            "model": Config.GROQ_VERSATILE_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 4096
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.groq.com/openai/v1/chat/completions", 
                    headers=headers, 
                    json=payload, 
                    timeout=120
                )
                response.raise_for_status()
                data = response.json()
                return data["choices"][0]["message"]["content"].strip()
        except httpx.TimeoutException:
            raise Exception("Request timed out. Please try with a smaller document.")
        except httpx.HTTPStatusError as e:
            raise Exception(f"API error: {e.response.status_code}")
        except Exception as e:
            raise Exception(f"Failed to generate response: {str(e)}")

    async def generate_ans_paper_text(self, raw_text: str) -> str:
        """Generate answers/solutions for questions extracted from PDF."""
        prompt = f"""You are an expert academic solution generator.

Your task is to:
1. Identify each distinct question from the following text.
2. Provide a detailed and accurate solution to each question.
3. Format your response such that each question is followed immediately by its solution.

For every question:
- Start with:
    Question <number>:
    <Full question text>

- Then give:
    Solution <number>
    <Answer formatted as per marking scheme below>

Answer formatting rules based on marks:
- If the question is of **1 mark**, give a **single-line concise explanation**.
- If the question is of **2 or 3 marks**, give the answer in **3 distinct and clear points** (use bulleted format only).
- If the question is of **4 or more marks**, structure your answer into **5 detailed and logical bullet points**.

Please ensure that:
- Sub-parts of a question (like (a), (b), etc.) are included within the same question block.
- Explanations are clear, precise, and maintain academic tone.
- Use correct mathematical notation and formatting where applicable. For mathematical expressions, use KaTeX syntax
  (e.g., $$...$$ for display math and $...$ for inline math).
- You do not skip any questions.

Now, here is the question paper text:

{raw_text}

Give your output in the same format as the input."""
        return await self._query_groq(prompt)

    async def generate_question_paper_text(self, raw_text: str) -> str:
        """Generate a similar question paper based on the input."""
        prompt = f"""You are an expert question paper generator. Given the input question paper in a structured format, generate a new question paper that:
- Has the same structure
- Covers the same curriculum or topic
- Uses different wording and questions (same difficulty level)
- Keeps the same marks per question

Here is the input:

{raw_text}

Give your output in the same format as the input."""
        return await self._query_groq(prompt)

    def text_to_formatted_pdf(self, text: str, filename: str = "generated_pdf.pdf") -> dict:
        """Convert text to a formatted PDF document."""
        print_memory_usage("before text_to_formatted_pdf call")
        
        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=A4)
        width, height = A4
        x_margin = 50
        y = height - 50
        line_height = 14
        font_size = 11

        initial_lines = text.split('\n')
        lines = self.split_lines_to_fit_page(initial_lines)

        for i, line in enumerate(lines):
            clean_line = line.strip()
            if i < 5 and clean_line:
                c.setFont("Times-Bold", 14)
                text_width = c.stringWidth(clean_line, "Times-Bold", 14)
                c.drawString((width - text_width) / 2, y, clean_line)
                y -= line_height
            elif any(clean_line.lower().startswith(p) for p in ["part", "section", "instructions", "questions", "question", "solution"]):
                c.setFont("Times-Bold", 12)
                c.drawString(x_margin, y, clean_line)
                y -= line_height
            elif clean_line == "":
                y -= line_height // 2
            else:
                c.setFont("Times-Roman", font_size)
                c.drawString(x_margin, y, clean_line)
                y -= line_height

            if y < 50:
                c.showPage()
                y = height - 50
                c.setFont("Times-Roman", font_size)

        c.save()
        buffer.seek(0)
        print_memory_usage("after text_to_formatted_pdf call")
        return {"text": lines, "pdf_file": buffer}

    def wrap_text(self, text: str, canvas_obj, font_name: str, font_size: int, max_width: float) -> list:
        """Wrap text to fit within a given width."""
        words = text.split()
        lines = []
        current_line = ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            if canvas_obj.stringWidth(test_line, font_name, font_size) <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    def split_lines_to_fit_page(self, lines: list, font_name: str = "Times-Roman", font_size: int = 11, page_size=A4, margin: int = 50) -> list:
        """Split lines to fit within page width."""
        dummy_canvas = canvas.Canvas(os.path.join(self.temp_dir, "dummy.pdf"))
        page_width, _ = page_size
        usable_width = page_width - 2 * margin
        fitted_lines = []
        for line in lines:
            if line.strip() == "":
                fitted_lines.append("")
            else:
                wrapped = self.wrap_text(line, dummy_canvas, font_name, font_size, usable_width)
                fitted_lines.extend(wrapped)
        return fitted_lines

    def _cleanup_temp_images(self, num_pages: int, session_id: str):
        """Clean up temporary image files for a specific session."""
        for i in range(num_pages):
            path = os.path.join(self.temp_dir, f"{session_id}_Page_{i+1}.jpg")
            try:
                if os.path.exists(path):
                    os.remove(path)
            except Exception as e:
                print(f"Error cleaning up {path}: {e}")

    async def generate_question_paper(self, pdf_path: str) -> dict:
        """Generate a similar question paper from uploaded PDF."""
        num_pages = 0
        session_id = str(uuid.uuid4())  # Unique ID for this request
        try:
            num_pages = await self.pdf_to_images(pdf_path, session_id)
            text = await self.extract_text(num_pages, session_id)
            
            if not text.strip():
                return {
                    "text": "I couldn't extract any text from your PDF. Please make sure the PDF contains readable text or try with a clearer image.",
                    "pdf_file": None
                }
            
            generated_text = await self.generate_question_paper_text(text)
            return self.text_to_formatted_pdf(generated_text)
        except Exception as e:
            print(f"Error generating question paper: {e}")
            return {
                "text": f"I encountered an error while processing your question paper: {str(e)}\n\nPlease try again with a different file or a clearer scan.",
                "pdf_file": None
            }
        finally:
            if num_pages > 0:
                self._cleanup_temp_images(num_pages, session_id)

    async def generate_ans_paper(self, pdf_path: str) -> dict:
        """Generate solutions for questions from uploaded PDF."""
        num_pages = 0
        session_id = str(uuid.uuid4())  # Unique ID for this request
        try:
            num_pages = await self.pdf_to_images(pdf_path, session_id)
            text = await self.extract_text(num_pages, session_id)
            
            if not text.strip():
                return {
                    "text": "I couldn't extract any text from your PDF. Please make sure the PDF contains readable text or try with a clearer image.",
                    "pdf_file": None
                }
            
            generated_text = await self.generate_ans_paper_text(text)
            return self.text_to_formatted_pdf(generated_text)
        except Exception as e:
            print(f"Error generating answer paper: {e}")
            return {
                "text": f"I encountered an error while solving your questions: {str(e)}\n\nPlease try again with a different file or a clearer scan.",
                "pdf_file": None
            }
        finally:
            if num_pages > 0:
                self._cleanup_temp_images(num_pages, session_id)
