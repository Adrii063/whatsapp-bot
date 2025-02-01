from ai_client import ai_client
from conversation import conversation_manager
from reservations import reservation_manager
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from config import PORT

app = Flask(__name__)

def chat_with_ai(user_input, user_id):
    """Maneja la conversación personalizada para cada usuario"""
    conversation_manager.add_message(user_id, "user", user_input)
    response = ai_client.chat(conversation_manager.get_history(user_id))
    conversation_manager.add_message(user_id, "assistant", response)
    return response

def validate_user_input(user_input):
    """Corrige errores comunes o reformula preguntas antes de enviarlas a la IA."""
    corrections = {
        "reserva mesa": "quiero reservar una mesa",
        "quiero reservar": "quiero reservar una mesa",
        "menu": "¿Cuál es el menú de hoy?",
        "hora": "¿Cuál es el horario del restaurante?",
        "gracias": "¡Gracias! 😊"
    }
    
    for key, correction in corrections.items():
        if key in user_input:
            return correction
    
    return user_input

@app.route("/")
def home():
    return "¡El bot está funcionando!"

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.values.get("Body", "").strip()
    user_id = request.values.get("From", "")

    print(f"📩 Mensaje de {user_id}: {incoming_msg}")

    # Manejo de cancelaciones
    if incoming_msg.lower() in ["cancelar", "cancela", "anular", "eliminar reserva"]:
        response_text = "❌ Tu reserva ha sido cancelada." if user_id in reservation_manager.user_reservations else "⚠️ No tienes reservas activas."
    
    # Manejo de reservas
    elif "reservar" in incoming_msg.lower():
        response_text = reservation_manager.handle_reservation(user_id, incoming_msg)

    # Chat con IA
    else:
        response_text = chat_with_ai(incoming_msg, user_id)

    print(f"📤 Respuesta a {user_id}: {response_text}")
    
    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)