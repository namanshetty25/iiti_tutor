import os
import io
import asyncio
import json
import httpx
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

    async def pdf_to_images(self, pdf_path):
        print_memory_usage("before pdf_to_images call")
        doc = fitz.open(pdf_path)
        num_pages = len(doc)
        
        for i in range(num_pages):
            page = doc.load_page(i)
            # Higher resolution (300 DPI) for better OCR
            pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
            path = os.path.join(self.temp_dir, f"Page_{i+1}.jpg")
            pix.save(path)
            print(f"Saved: {path}")
            
        print_memory_usage("after pdf_to_images call")
        return num_pages

    async def extract_text(self, num):
        print_memory_usage("before extract_text call")
        async def process_image(i):
            path = os.path.join(self.temp_dir, f"Page_{i+1}.jpg")
            image = Image.open(path)
            return pytesseract.image_to_string(image)
        
        tasks = [process_image(i) for i in range(num)]
        texts = await asyncio.gather(*tasks)
        text = "\n".join(texts)
        print_memory_usage("after extract_text call")
        return text

    async def _query_groq(self, prompt):
        payload = {
            "model": Config.GROQ_VERSATILE_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 2048
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient() as client:
            response = await client.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

    async def generate_ans_paper_text(self, raw_text):
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

    async def generate_question_paper_text(self, raw_text):
        prompt = f"""You are an expert question paper generator. Given the input question paper in a structured format, generate a new question paper that:
- Has the same structure
- Covers the same curriculum or topic
- Uses different wording and questions (same difficulty level)
- Keeps the same marks per question

Here is the input:

{raw_text}

Give your output in the same format as the input."""
        return await self._query_groq(prompt)

    def text_to_formatted_pdf(self, text, filename="generated_pdf.pdf"):
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
            elif any(clean_line.lower().startswith(p) for p in ["part", "section", "instructions", "questions"]):
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

    def wrap_text(self, text, canvas_obj, font_name, font_size, max_width):
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

    def split_lines_to_fit_page(self, lines, font_name="Times-Roman", font_size=11, page_size=A4, margin=50):
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

    async def generate_question_paper(self, pdf_path):
        num = await self.pdf_to_images(pdf_path)
        text = await self.extract_text(num)
        generated_text = await self.generate_question_paper_text(text)
        return self.text_to_formatted_pdf(generated_text)

    async def generate_ans_paper(self, pdf_path):
        num = await self.pdf_to_images(pdf_path)
        text = await self.extract_text(num)
        generated_text = await self.generate_ans_paper_text(text)
        return self.text_to_formatted_pdf(generated_text)
