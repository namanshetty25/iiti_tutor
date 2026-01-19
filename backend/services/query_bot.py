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

        # Initialized in initialize() method
        self.chunks = []
        self.metadata = []
        self.index = None
        self.model = None
        self.embeddings = None
        self._initialized = False

    async def initialize(self, db):
        """Initialize the query bot with course data from database."""
        try:
            self.chunks, self.metadata = await self.load_course_chunks(db)
            if self.chunks:
                self.index, self.model, self.embeddings = self.build_faiss_index(self.chunks)
                self._initialized = True
                print(f"QueryBot initialized with {len(self.chunks)} chunks")
            else:
                print("Warning: No course chunks loaded - QueryBot will have limited functionality")
        except Exception as e:
            print(f"Error initializing QueryBot: {e}")
            self._initialized = False

    async def load_course_chunks(self, db):
        """Load course data from MongoDB and create searchable chunks."""
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
        """Build FAISS index for semantic search."""
        print_memory_usage("before build_faiss_index call")
        model = SentenceTransformer(self.EMBEDDING_MODEL)
        embeddings = model.encode(chunks, show_progress_bar=True)
        index = faiss.IndexFlatL2(len(embeddings[0]))
        index.add(np.array(embeddings))
        print_memory_usage("after build_faiss_index call")
        return index, model, embeddings

    def extract_course_code(self, query: str, chat_history: list = None) -> str | None:
        """Extract course code from query or chat history."""
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

    def get_chunks_by_course_code(self, course_code: str) -> list:
        """Get all chunks for a specific course code."""
        course_code_clean = course_code.upper().replace(" ", "")
        chunks_found = []
        for i, chunk in enumerate(self.chunks):
            code_in_chunk = self.metadata[i]["course"].upper().replace(" ", "")
            if course_code_clean in code_in_chunk:
                chunks_found.append((chunk, self.metadata[i]))
        return chunks_found

    def retrieve_relevant_chunks(self, query: str, chat_history: list = None, top_k: int = 4) -> list:
        """Retrieve relevant chunks for a query using semantic search."""
        # Safety check - ensure initialization
        if not self._initialized or self.index is None or self.model is None:
            print("Warning: QueryBot not properly initialized")
            return []
        
        if not self.chunks:
            return []
            
        # First try exact course code matching
        course_code = self.extract_course_code(query, chat_history)
        if course_code:
            chunks_for_course = self.get_chunks_by_course_code(course_code)
            if chunks_for_course:
                return chunks_for_course[:top_k]

        # Fall back to semantic search
        try:
            query_vec = self.model.encode([query])
            D, I = self.index.search(query_vec, top_k)
            return [(self.chunks[i], self.metadata[i]) for i in I[0] if i < len(self.chunks)]
        except Exception as e:
            print(f"Error in semantic search: {e}")
            return []

    async def query_llama(self, query: str, context_chunks: list, chat_history: list = None) -> dict:
        """Query the LLM with context from retrieved chunks."""
        try:
            context = "\n\n".join(f"Chunk: {chunk}" for chunk, meta in context_chunks)
            
            messages = [
                {
                    "role": "system", 
                    "content": "You are a helpful academic assistant for IIT Indore (IITI) students. "
                              "Use the following course data to answer questions accurately. "
                              "If the information isn't in the provided context, say so clearly. "
                              "Be concise but thorough in your explanations."
                }
            ]

            if chat_history:
                messages.extend(chat_history)

            messages.append({"role": "user", "content": f"{context}\n\nQuestion: {query}"})

            payload = {
                "model": self.MODEL_NAME,
                "messages": messages,
                "temperature": 0.2,
                "max_tokens": 1024
            }

            headers = {
                "Authorization": f"Bearer {self.GROQ_API_KEY}",
                "Content-Type": "application/json"
            }

            async with httpx.AsyncClient() as client:
                response = await client.post(self.GROQ_API_URL, headers=headers, json=payload, timeout=30)
                response.raise_for_status()
                data = response.json()
                return {
                    "text": data["choices"][0]["message"]["content"].strip(),
                    "pdf_file": None
                }
        except httpx.TimeoutException:
            return {
                "text": "The request took too long. Please try again with a simpler question.",
                "pdf_file": None
            }
        except httpx.HTTPStatusError as e:
            print(f"API error: {e}")
            return {
                "text": "I encountered an error while processing your question. Please try again.",
                "pdf_file": None
            }
        except Exception as e:
            print(f"Query error: {e}")
            return {
                "text": "I had trouble answering your question. Please try rephrasing it or ask about a specific course code.",
                "pdf_file": None
            }
