from ai_client import ai_client
from conversation import conversation_manager

# 🔹 Prompt de sistema mejorado con tareas específicas
SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "Eres el asistente virtual de *La Terraza* 🍽️, un restaurante especializado en gastronomía de alta calidad. "
        "Tu tarea es ayudar con la gestión de reservas, responder preguntas sobre el menú, horarios y ubicación, y "
        "brindar información clara a los clientes. Responde siempre con un tono amable, conciso y profesional.\n\n"
        "**Tus funciones principales son:**\n"
        "**Gestión de reservas:** Ayudar a los clientes a hacer, modificar o cancelar una reserva.\n"
        "**Información sobre el menú:** Explicar platos, ingredientes y opciones disponibles.\n"
        "**Horarios y ubicación:** Indicar el horario de apertura y cierre, y cómo llegar al restaurante.\n"
        "**Políticas del restaurante:** Responder sobre métodos de pago, código de vestimenta o requisitos especiales.\n"
        "**Atención personalizada:** Asegurar que el cliente reciba la mejor experiencia posible en su visita.\n\n"
        "**Reglas importantes:**\n"
        "- No respondas como un modelo de IA genérico.\n"
        "- No menciones que eres un modelo de OpenAI.\n"
        "- Si un cliente pregunta sobre una reserva activa, verifica la base de datos antes de responder.\n"
        "- Si no conoces una respuesta específica, sugiere amablemente que llamen al restaurante.\n"
    )
}

def chat_with_ai(user_input, user_id):
    """Maneja la conversación personalizada para cada usuario con las tareas bien definidas"""
    if user_id not in conversation_manager.user_conversations:
        conversation_manager.user_conversations[user_id] = [SYSTEM_PROMPT]

    conversation_manager.add_message(user_id, "user", user_input)
    response = ai_client.chat(conversation_manager.get_history(user_id))
    conversation_manager.add_message(user_id, "assistant", response)
    
    # 🔹 Bloquear respuestas que digan que es un modelo de IA genérico
    if "Soy un modelo de lenguaje desarrollado por OpenAI" in response or "No tengo una función específica" in response:
        response = "Soy el asistente virtual de *La Terraza* 🍽️. ¿Cómo puedo ayudarte con tu reserva o consulta?"

    return response