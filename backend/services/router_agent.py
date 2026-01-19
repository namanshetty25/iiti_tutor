import httpx
import os
import json
from core.config import Config
from services.query_bot import QueryBot
from services.question_bot import QuestionPaperBot
from services.scheduler_bot import Scheduler
from services.history import ChatHistoryManager

class RouterAgent:
    def __init__(self, db, groq_api_key=Config.GROQ_API_KEY, model=Config.GROQ_MODEL):
        self.api_key = groq_api_key
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = model
        self.db = db
        self.history_manager = ChatHistoryManager(db)
        
        # Bots
        self.query_bot = QueryBot(groq_api_key=groq_api_key)
        self.question_bot = QuestionPaperBot(groq_api_key=groq_api_key)
        self.scheduler_bot = Scheduler(api_key=groq_api_key)

    async def initialize_bots(self):
        await self.query_bot.initialize(self.db)

    async def classify_prompt(self, user_prompt: str) -> str:
        """Classify user prompt into one of the bot categories."""
        system_prompt = (
            "You are an intelligent routing assistant for NEXUS, an AI academic tutor for IITI students. "
            "Classify the user's prompt into exactly one of the following categories:\n\n"
            
            "1. **general** - Use this for:\n"
            "   - Greetings like 'hi', 'hello', 'hey', 'good morning'\n"
            "   - Help requests like 'what can you do?', 'help me', 'how does this work?'\n"
            "   - Thanks or farewells like 'thanks', 'bye', 'goodbye'\n"
            "   - Off-topic or casual conversation\n"
            "   - Unclear or ambiguous queries that don't fit other categories\n\n"
            
            "2. **questionpaper** - Use this if the user wants to:\n"
            "   - Generate sample questions based on a question paper\n"
            "   - Get solutions to questions from a PDF\n"
            "   - Solve questions from a document\n"
            "   - Answer or analyze questions from an uploaded file\n\n"
            
            "3. **scheduler** - Use this if the user wants to:\n"
            "   - Create a study plan\n"
            "   - Generate a weekly/daily schedule\n"
            "   - Organize time for exams, assignments, or productivity\n\n"
            
            "4. **query** - Use this if the user is asking academic queries such as:\n"
            "   - Course codes (e.g., EE101, CS202)\n"
            "   - Curriculum details or semester-wise subjects\n"
            "   - Recommended books or reading material\n"
            "   - Specific topics covered in a course\n"
            "   - Syllabus-related information\n\n"
            
            "Return only one of these exact values: general, questionpaper, scheduler, or query.\n"
            "Do not explain your reasoning. Just return the category label."
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 10
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.api_url, headers=headers, json=payload, timeout=20)
                response.raise_for_status()
                data = response.json()
                classification = data["choices"][0]["message"]["content"].strip().lower()
                # Validate classification
                valid_categories = ["general", "questionpaper", "scheduler", "query"]
                if classification not in valid_categories:
                    return "general"  # Default to general for unrecognized classifications
                return classification
        except Exception as e:
            print(f"Classification error: {e}")
            return "general"  # Default to general on error

    async def classify_question_action(self, prompt: str) -> str:
        """Determine if user wants to solve or generate questions."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        classification_prompt = f"""
        Analyze the user's prompt and determine if they want to:
        1. "answer" - Solve the questions, provide solutions, explain answers, or "solve" the paper.
        2. "generate" - Create a new/similar paper, generate more questions, or make another set.

        Rules:
        - If the user says 'solve', 'answer', 'solutions', 'explain', or 'give answers' -> return "answer"
        - If the user says 'generate', 'create similar', 'make another', 'new paper' -> return "generate"
        - If the user just uploads a file or it's ambiguous -> return "answer" as it's the more common request.

        Return ONLY the word "answer" or "generate".
        Prompt: {prompt}
        """
        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": classification_prompt}],
            "temperature": 0.1,
            "max_tokens": 10
        }
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.api_url, headers=headers, json=payload, timeout=20)
                response.raise_for_status()  # Fixed: Was missing this
                data = response.json()
                action = data["choices"][0]["message"]["content"].strip().lower()
                print(f"DEBUG: PDF Action Classification for '{prompt}' -> {action}")
                return action
        except Exception as e:
            print(f"Question action classification error: {e}")
            return "answer"  # Default to answer on error

    async def handle_general_query(self, user_prompt: str, chat_history: list = None) -> dict:
        """Handle general conversation, greetings, help requests, etc."""
        system_prompt = """You are NEXUS, a friendly and helpful AI academic tutor for the IIT Indore (IITI) community.

Your capabilities include:
1. **Academic Navigator** - Answer questions about course codes (e.g., EE101, CS202), syllabus, curriculum, and recommended books
2. **Smart Scheduler** - Create personalized study plans and schedules based on user tasks and time constraints
3. **Exam Assistant** - Solve question papers (upload PDF) or generate similar practice papers

When responding:
- Be friendly, helpful, and encouraging
- Keep responses concise but informative
- If the user seems to need one of your specific capabilities, guide them to use it
- For greetings, introduce yourself briefly and ask how you can help
- For help requests, explain your capabilities clearly

You are specifically designed for IITI students, so be aware of their academic context."""

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                *([msg for msg in chat_history] if chat_history else []),
                {"role": "user", "content": user_prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 500
        }

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.api_url, headers=headers, json=payload, timeout=20)
                response.raise_for_status()
                data = response.json()
                return {
                    "text": data["choices"][0]["message"]["content"].strip(),
                    "pdf_file": None
                }
        except Exception as e:
            print(f"General query error: {e}")
            return {
                "text": "Hello! I'm NEXUS, your AI academic tutor. I can help you with course information, study schedules, and question papers. How can I assist you today?",
                "pdf_file": None
            }

    async def route(self, user_prompt: str, user_id: str, conversation_id: str, file_path=None):
        """Route the user query to the appropriate bot."""
        query_type = await self.classify_prompt(user_prompt)
        chat_history = await self.history_manager.load_history(user_id, conversation_id)
        
        await self.history_manager.save_message(user_id, conversation_id, "user", user_prompt)
        
        result = None
        
        # Handle general conversation
        if query_type == "general":
            result = await self.handle_general_query(user_prompt, chat_history)
        
        # Handle question paper requests
        elif query_type == "questionpaper":
            if file_path:
                action = await self.classify_question_action(user_prompt)
                if "answer" in action or "solve" in action:
                    result = await self.question_bot.generate_ans_paper(file_path)
                else:
                    result = await self.question_bot.generate_question_paper(file_path)
            else:
                # No file provided - give helpful message
                result = {
                    "text": "I'd be happy to help with your question paper! 📄\n\n"
                           "To solve questions or generate a similar paper, please:\n"
                           "1. Click the 📎 attachment button below\n"
                           "2. Upload your question paper PDF\n"
                           "3. Tell me if you want me to **solve** the questions or **generate** a similar paper\n\n"
                           "Once you upload the file, I'll get right to work!",
                    "pdf_file": None
                }
        
        # Handle scheduler requests
        elif query_type == "scheduler":
            result = await self.scheduler_bot.run_scheduler(user_prompt)
        
        # Handle academic queries (default)
        else:
            relevant_chunks = self.query_bot.retrieve_relevant_chunks(user_prompt, chat_history)
            if relevant_chunks:
                result = await self.query_bot.query_llama(user_prompt, relevant_chunks, chat_history)
            else:
                # No relevant chunks found - provide helpful response
                result = {
                    "text": "I couldn't find specific information about that in our curriculum database. "
                           "Could you please:\n"
                           "- Mention the specific course code (e.g., EE101, CS202)\n"
                           "- Or ask about a specific topic from the IITI curriculum\n\n"
                           "I'm here to help with course information, syllabus details, and recommended books!",
                    "pdf_file": None
                }

        # Save bot response to history
        if result and result.get("text"):
            text_to_save = result["text"]
            if isinstance(text_to_save, list):
                text_to_save = "\n".join(text_to_save)
            await self.history_manager.save_message(user_id, conversation_id, "assistant", text_to_save)

        return result
