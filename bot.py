from ai_client import ai_client
from conversation import conversation_manager

def chat_with_ai(user_input, user_id):
    """Maneja la conversación personalizada para cada usuario"""
    conversation_manager.add_message(user_id, "user", user_input)
    response = ai_client.chat(conversation_manager.get_history(user_id))
    conversation_manager.add_message(user_id, "assistant", response)
    return response