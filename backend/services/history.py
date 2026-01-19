from datetime import datetime, timezone

class ChatHistoryManager:
    def __init__(self, db):
        self.db = db
        self.collection = self.db["chat_history"]

    async def save_message(self, user_id: str, conversation_id: str, role: str, message_content: str):
        message = {
            "user_id": user_id,
            "conversation_id": conversation_id,
            "role": role,
            "content": message_content,
            "timestamp": datetime.now(timezone.utc)
        }
        try:
            await self.collection.insert_one(message)
        except Exception as e:
            print(f"Database save error: {str(e)}")
            raise

    async def load_history(self, user_id: str, conversation_id: str, limit: int = 10) -> list[dict]:
        try:
            cursor = self.collection.find(
                {"user_id": user_id, "conversation_id": conversation_id},
                projection={"role": 1, "content": 1, "_id": 0}
            ).sort("timestamp", -1).limit(limit)
            
            history = [doc async for doc in cursor]
            return history[::-1]
        except Exception as e:
            print(f"Error loading history: {e}")
            return []
