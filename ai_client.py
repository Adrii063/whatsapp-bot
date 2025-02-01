import openai
from config import OPENAI_API_KEY, BASE_URL

class AIClient:
    def __init__(self):
        self.client = openai.OpenAI(api_key=OPENAI_API_KEY, base_url=BASE_URL)

    def chat(self, messages):
        response = self.client.chat.completions.create(
            model="openai/gpt-4o",
            messages=messages,
            max_tokens=300,
            temperature=0.7
        )
        return response.choices[0].message.content if response.choices else "No se pudo obtener respuesta."

ai_client = AIClient()