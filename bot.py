from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from ai_client import ai_client
from conversation import conversation_manager
from reservations import reservation_manager
from config import PORT

app = Flask(__name__)

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
        conversation_manager.add_message(user_id, "user", incoming_msg)
        response_text = ai_client.chat(conversation_manager.get_history(user_id))
        conversation_manager.add_message(user_id, "assistant", response_text)

    print(f"📤 Respuesta a {user_id}: {response_text}")
    
    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)