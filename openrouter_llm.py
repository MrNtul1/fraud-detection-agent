import os
from openai import AsyncOpenAI

class OpenRouterLLM:
    def __init__(self):
        # OpenRouter uses the OpenAI-compatible client
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY")
        )
        self.model = "meta-llama/llama-3.1-70b-instruct"

    async def generate_str(self, message: str):
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": message}]
        )
        return response.choices[0].message.content