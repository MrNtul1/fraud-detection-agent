import os
import google.generativeai as genai

# Load API key
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")


class GeminiLLM:

    async def generate_str(self, message: str):

        response = model.generate_content(message)

        return response.text