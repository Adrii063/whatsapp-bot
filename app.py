from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import logging
from dotenv import load_dotenv
import os
from reservations import reservation_manager
from bot import chat_with_ai

# Cargar variables de entorno
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ ERROR: La variable de entorno OPENAI_API_KEY no está configurada.")

# Configurar logs
logging.basicConfig(level=logging.INFO)

# Inicializar Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ El bot está funcionando correctamente. Usa /whatsapp para interactuar."

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    """
    Maneja los mensajes de WhatsApp y decide qué acción tomar (IA o reserva).
    """
    incoming_msg = request.values.get("Body", "").strip()
    user_id = request.values.get("From", "")

    logging.info(f"📩 Mensaje recibido de {user_id}: {incoming_msg}")

    # 🔹 Consultar reservas activas
    if "qué reservas tengo" in incoming_msg.lower() or "tengo alguna reserva" in incoming_msg.lower():
        response_text = reservation_manager.get_user_reservation(user_id)

    # 🔹 Cancelar reserva
    elif any(phrase in incoming_msg.lower() for phrase in ["cancelar", "cancela", "anular", "eliminar reserva"]):
        response_text = reservation_manager.cancel_reservation(user_id)

    # 🔹 Hacer una nueva reserva
    elif "reservar" in incoming_msg.lower() or "quiero una mesa" in incoming_msg.lower():
        response_text = reservation_manager.handle_reservation(user_id, incoming_msg)

    # 🔹 Conversación normal con la IA
    else:
        response_text = chat_with_ai(incoming_msg, user_id)

    logging.info(f"📤 Respuesta enviada a {user_id}: {response_text}")

    # Enviar respuesta a WhatsApp
    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logging.info(f"🚀 Servidor iniciado en el puerto {port}")
    app.run(host="0.0.0.0", port=port)