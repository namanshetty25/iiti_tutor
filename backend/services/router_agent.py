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
        system_prompt = (
            "You are an intelligent routing assistant. Classify the user's prompt into exactly one of the following categories:\n\n"
            "1. questionpaper - Use this if the user wants to:\n"
            "   - Generate sample questions based on a question paper\n"
            "   - Get solutions to questions from a PDF\n"
            "   - Solve this\n"
            "   - Answer or solve questions from a document\n\n"
            "2. scheduler - Use this if the user wants to:\n"
            "   - Create a study plan\n"
            "   - Generate a weekly/daily schedule\n"
            "   - Organize time for exams, assignments, or productivity\n\n"
            "3. query - Use this if the user is asking academic queries such as:\n"
            "   - Course codes (e.g., EE101, CS202)\n"
            "   - Curriculum details or semester-wise subjects\n"
            "   - Recommended books or reading material\n"
            "   - Specific topics covered in a course\n"
            "   - Syllabus-related information\n\n"
            "Return only one of these exact values: questionpaper, scheduler, or query.\n"
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

        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_url, headers=headers, json=payload, timeout=20)
            response.raise_for_status()
            data = response.json()
            classification = data["choices"][0]["message"]["content"].strip().lower()
            return classification

    async def classify_question_action(self, prompt):
        headers = {"Authorization": f"Bearer {self.api_key}"}
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
        async with httpx.AsyncClient() as client:
            response = await client.post(self.api_url, headers=headers, json=payload, timeout=20)
            data = response.json()
            action = data["choices"][0]["message"]["content"].strip().lower()
            print(f"DEBUG: PDF Action Classification for '{prompt}' -> {action}")
            return action

    async def route(self, user_prompt: str, user_id: str, conversation_id: str, file_path=None):
        query_type = await self.classify_prompt(user_prompt)
        chat_history = await self.history_manager.load_history(user_id, conversation_id)
        
        await self.history_manager.save_message(user_id, conversation_id, "user", user_prompt)
        
        result = None
        if query_type == "questionpaper" and file_path:
            action = await self.classify_question_action(user_prompt)
            if "answer" in action or "solve" in action:
                result = await self.question_bot.generate_ans_paper(file_path)
            else:
                result = await self.question_bot.generate_question_paper(file_path)
        elif query_type == "scheduler":
            result = await self.scheduler_bot.run_scheduler(user_prompt)
        else: # Default to query
            relevant_chunks = self.query_bot.retrieve_relevant_chunks(user_prompt, chat_history)
            result = await self.query_bot.query_llama(user_prompt, relevant_chunks, chat_history)

        if result and result.get("text"):
            text_to_save = result["text"]
            if isinstance(text_to_save, list):
                text_to_save = "\n".join(text_to_save)
            await self.history_manager.save_message(user_id, conversation_id, "assistant", text_to_save)

        return result
