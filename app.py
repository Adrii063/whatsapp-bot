from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import logging
import os
from bot import chat_with_ai
from reservations import reservation_manager

# Cargar variables de entorno
load_dotenv()

# Configuración de logs
logging.basicConfig(level=logging.INFO)

api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ ERROR: La variable de entorno OPENAI_API_KEY no está configurada.")

# Inicializar Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ El bot está funcionando correctamente. Usa /whatsapp para interactuar."

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    """Maneja los mensajes de WhatsApp y gestiona reservas y preguntas con IA"""
    incoming_msg = request.values.get("Body", "").strip()
    user_id = request.values.get("From", "")

    logging.info(f"📩 Mensaje recibido de {user_id}: {incoming_msg}")

    # ✅ Detectar intención de reservas
    if "reservar" in incoming_msg.lower() or "quiero una mesa" in incoming_msg.lower():
        response_text = reservation_manager.handle_reservation(user_id, incoming_msg)
    
    # ✅ Conversación con la IA
    else:
        response_text = chat_with_ai(incoming_msg, user_id)

    # Log de la respuesta
    logging.info(f"📤 Respuesta enviada a {user_id}: {response_text}")

    # Responder con Twilio
    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logging.info(f"🚀 Servidor iniciado en el puerto {port}")
    app.run(host="0.0.0.0", port=port)