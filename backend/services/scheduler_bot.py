import httpx
from core.config import Config

class Scheduler:
    def __init__(self, api_key: str = Config.GROQ_API_KEY, model_name: str = Config.GROQ_MODEL):
        self.GROQ_API_KEY = api_key
        self.MODEL_NAME = model_name
        self.GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
        self.TIME_ZONE = "Asia/Kolkata"

    async def _query_groq(self, prompt: str, max_tokens: int = 2048, temperature: float = 0.7) -> str:
        """Query Groq API for schedule generation."""
        headers = {
            "Authorization": f"Bearer {self.GROQ_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.MODEL_NAME,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(self.GROQ_API_URL, headers=headers, json=payload, timeout=30)
            response.raise_for_status()
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()

    def build_schedule_prompt(self, task_description: str) -> str:
        """Builds a flexible prompt for schedule generation with explicit formatting."""
        return f"""
You are an expert productivity assistant. Your task is to create a structured and realistic schedule based on the user's request provided below.

**--- INSTRUCTIONS ---**

1.  **Analyze the Request:** Carefully read the user's request inside the `<user_request>` tags to understand:
    *   The total duration for the schedule (e.g., "3 days," "a week," "today").
    *   A complete list of all tasks to be scheduled.
    *   Specific constraints, such as wake-up/sleep times, task durations, daily recurring tasks, and appointments.
    *   If wake-up/sleep times are not stated, assume 8:00 AM wake-up and 10:30 PM sleep.

2.  **Create a Logical Schedule:**
    *   Distribute all tasks logically across the specified number of days.
    *   Include realistic time for meals (lunch around 1-2 PM, dinner around 8-9 PM) and short breaks.
    *   The schedule for each day MUST start at the wake-up time and end at the sleep time.
    *   Time slots must be contiguous.

3.  **Output Format (Follow EXACTLY):**
    *   The entire output must be only the schedule. Do not add any conversational text, summaries, or explanations.
    *   The format must match this example precisely:

📅 Your Personalized Schedule
============================================================
Note: This schedule assumes a wake-up time of 8:00 AM and a sleep time of 10:30 PM unless specified otherwise in the request.

🗓 DAY 1
----------------------------------------
Time                 | Task
----------------------------------------
8:00 AM - 9:00 AM    | Morning Routine & Breakfast
9:00 AM - 12:00 PM   | Deep Work Block (e.g., Task 1)
12:00 PM - 1:00 PM   | Lunch Break
...
9:30 PM - 10:30 PM   | Wind down

🗓 DAY 2
----------------------------------------
Time                 | Task
----------------------------------------
8:00 AM - 9:00 AM    | Morning Routine & Breakfast
... and so on for all required days.

**--- USER REQUEST ---**

<user_request>
{task_description}
</user_request>

Now, generate the schedule based on all the rules and the exact format described above.
"""

    async def run_scheduler(self, initial_prompt: str) -> dict:
        """Run the scheduler to generate a study/productivity schedule."""
        try:
            llm_prompt = self.build_schedule_prompt(initial_prompt)
            formatted_schedule = await self._query_groq(llm_prompt)
            return {"text": formatted_schedule, "pdf_file": None}
        except httpx.TimeoutException:
            return {
                "text": "I'm taking too long to generate your schedule. Please try with a simpler request or fewer tasks.",
                "pdf_file": None
            }
        except httpx.HTTPStatusError as e:
            return {
                "text": f"I encountered an error while generating your schedule. Please try again in a moment.",
                "pdf_file": None
            }
        except Exception as e:
            print(f"Scheduler error: {e}")
            return {
                "text": "I had trouble creating your schedule. Could you please provide more details about:\n"
                       "- What tasks you need to complete\n"
                       "- How many days you have\n"
                       "- Any specific time constraints\n\n"
                       "For example: 'Create a 3-day study plan for my physics and math exams'",
                "pdf_file": None
            }
