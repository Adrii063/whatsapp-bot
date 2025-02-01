import logging
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os
from bot import chat_with_ai
from reservations import reservation_manager
from utils import extract_reservation_details

# Configurar logs
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

# Cargar variables de entorno
load_dotenv()

# Verificar API Key
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ ERROR: La variable de entorno OPENAI_API_KEY no está configurada.")

# Inicializar Flask
app = Flask(__name__)

@app.route("/")
def home():
    logging.debug("✅ Endpoint '/' ha sido accedido")
    return "✅ El bot está funcionando correctamente."

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    """Maneja los mensajes de WhatsApp y gestiona reservas y preguntas con IA"""
    incoming_msg = request.values.get("Body", "").strip().lower()
    user_id = request.values.get("From", "")

    logging.debug(f"📩 Mensaje recibido de {user_id}: {incoming_msg}")

    # ✅ Procesar solicitud de reserva
    if "reservar" in incoming_msg or "quiero una mesa" in incoming_msg:
        date, time, people = extract_reservation_details(incoming_msg)
        if date and time and people:
            response_text = reservation_manager.handle_reservation(user_id, date, time, people)
        else:
            response_text = "¿Podrías proporcionarme la fecha, hora y número de personas para la reserva?"
    else:
        response_text = chat_with_ai(incoming_msg, user_id)

    logging.debug(f"📤 Respuesta enviada a {user_id}: {response_text}")

    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logging.info(f"🚀 Servidor iniciado en el puerto {port}")
    app.run(host="0.0.0.0", port=port)