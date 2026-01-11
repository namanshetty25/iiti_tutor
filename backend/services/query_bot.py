import json
import re
import faiss
import httpx
import numpy as np
from sentence_transformers import SentenceTransformer
from core.config import Config
from utils.memory import print_memory_usage

class QueryBot:
    def __init__(self, 
                 embedding_model=Config.SENTENCE_TRANSFORMER_MODEL,
                 groq_api_key=Config.GROQ_API_KEY,
                 model_name=Config.GROQ_MODEL,
                 groq_api_url="https://api.groq.com/openai/v1/chat/completions"):

        self.EMBEDDING_MODEL = embedding_model
        self.GROQ_API_KEY = groq_api_key
        self.MODEL_NAME = model_name
        self.GROQ_API_URL = groq_api_url

        # Note: In a real app, chunks might be pre-loaded or loaded per request
        # For simplicity during refactoring, keeping the structure similar
        # but chunks/index should ideally be initialized once at startup
        self.chunks = []
        self.metadata = []
        self.index = None
        self.model = None

    async def initialize(self, db):
        self.chunks, self.metadata = await self.load_course_chunks(db)
        if self.chunks:
            self.index, self.model, self.embeddings = self.build_faiss_index(self.chunks)

    async def load_course_chunks(self, db):
        try:
            collection = db["First_Year_Curriculum"]
            cursor = collection.find({})
            raw_courses = await cursor.to_list(length=1000)
            print(f"Found {len(raw_courses)} courses in database")
        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            raw_courses = []

        chunks = []
        metadata = []

        for course in raw_courses:
            code = course.get("Course Code", "")
            title = course.get("Course Title", course.get("Title", ""))
            full_text = f"{code}\n{title}\n"

            for k, v in course.items():
                if k in ["_id"]: continue
                if isinstance(v, list):
                    full_text += f"\n{k}:\n" + "\n".join(
                        item if isinstance(item, str) else str(item) for item in v
                    )
                elif isinstance(v, dict):
                    full_text += f"\n{k}:\n" + json.dumps(v)
                elif isinstance(v, str):
                    full_text += f"\n{k}: {v}"

            for paragraph in full_text.split("\n\n"):
                if len(paragraph.strip()) > 50:
                    chunks.append(paragraph.strip())
                    metadata.append({"course": code, "title": title})

        return chunks, metadata

    def build_faiss_index(self, chunks):
        print_memory_usage("before build_faiss_index call")
        model = SentenceTransformer(self.EMBEDDING_MODEL)
        embeddings = model.encode(chunks, show_progress_bar=True)
        index = faiss.IndexFlatL2(len(embeddings[0]))
        index.add(np.array(embeddings))
        print_memory_usage("after build_faiss_index call")
        return index, model, embeddings

    def extract_course_code(self, query: str, chat_history: list = None):
        match = re.search(r"\b([A-Z]{2,3}\s?\d{3}[A-Z]?)\b", query.upper())
        if match:
            return match.group(1).replace(" ", "")

        if chat_history:
            for msg in reversed(chat_history):
                if msg.get("role") == "user" and msg.get("content"):
                    history_match = re.search(r"\b([A-Z]{2,3}\s?\d{3}[A-Z]?)\b", msg["content"].upper())
                    if history_match:
                        return history_match.group(1).replace(" ", "")
        return None

    def get_chunks_by_course_code(self, course_code):
        course_code_clean = course_code.upper().replace(" ", "")
        chunks_found = []
        for i, chunk in enumerate(self.chunks):
            code_in_chunk = self.metadata[i]["course"].upper().replace(" ", "")
            if course_code_clean in code_in_chunk:
                chunks_found.append((chunk, self.metadata[i]))
        return chunks_found

    def retrieve_relevant_chunks(self, query, chat_history: list = None, top_k=4):
        if not self.index:
            return []
            
        course_code = self.extract_course_code(query, chat_history)
        if course_code:
            chunks_for_course = self.get_chunks_by_course_code(course_code)
            if chunks_for_course:
                return chunks_for_course[:top_k]

        query_vec = self.model.encode([query])
        D, I = self.index.search(query_vec, top_k)
        return [(self.chunks[i], self.metadata[i]) for i in I[0]]

    async def query_llama(self, query, context_chunks, chat_history: list = None):
        try:
            context = "\n\n".join(f"Chunk: {chunk}" for chunk, meta in context_chunks)
            messages = [{"role": "system", "content": "You are a helpful academic assistant. Use the following course data to answer questions."}]

            if chat_history:
                messages.extend(chat_history)

            messages.append({"role": "user", "content": f"{context}\n\nQuestion: {query}"})

            payload = {
                "model": self.MODEL_NAME,
                "messages": messages,
                "temperature": 0.2,
            }

            headers = {
                "Authorization": f"Bearer {self.GROQ_API_KEY}",
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(self.GROQ_API_URL, headers=headers, json=payload, timeout=20)
                response.raise_for_status()
                data = response.json()
                return {
                    "text": data["choices"][0]["message"]["content"].strip(),
                    "pdf_file": None
                }
        except Exception as e:
            raise Exception(f"Query failed: {str(e)}")
