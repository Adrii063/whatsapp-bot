import openai

# Configuración para usar OpenRouter en lugar de OpenAI
client = openai.OpenAI(
    api_key="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",  # Reemplázalo con tu API Key de OpenRouter
    base_url="https://openrouter.ai/api/v1"
)

def chat_with_ai(user_input):
    """
    Esta función envía un mensaje a OpenRouter y devuelve la respuesta.
    """
    response = client.chat.completions.create(
    model="liquid/lfm-7b",  # Usa el modelo DeepSeek R1
    messages=[{"role": "user", "content": user_input}],
    max_tokens=80
)

    return response.choices[0].message.content

# Probamos la función
while True:
    user_message = input("Tú: ")
    if user_message.lower() == "salir":
        break
    response = chat_with_ai(user_message)
    print("Chatbot:", response)
