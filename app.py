import logging
import sys

# Configurar logs para asegurarnos de que se imprimen en Render
logging.basicConfig(
    level=logging.DEBUG,  # Cambia a DEBUG para ver todos los logs
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)  # Asegura que los logs se envían a Render
    ]
)

logging.debug("🚀 Servidor Flask iniciado correctamente")

from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os
from bot import chat_with_ai
from reservations import reservation_manager

# Cargar variables de entorno
load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError("❌ ERROR: La variable de entorno OPENAI_API_KEY no está configurada.")

# Inicializar Flask
app = Flask(__name__)

@app.route("/")
def home():
    logging.debug("✅ Endpoint '/' ha sido accedido")
    return "✅ El bot está funcionando correctamente. Usa /whatsapp para interactuar."

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    """Maneja los mensajes de WhatsApp y gestiona reservas y preguntas con IA"""
    incoming_msg = request.values.get("Body", "").strip().lower()
    user_id = request.values.get("From", "")

    logging.debug(f"📩 Mensaje recibido de {user_id}: {incoming_msg}")

    # ✅ Consultar reservas activas
    if "qué reservas tengo" in incoming_msg or "tengo alguna reserva" in incoming_msg:
        response_text = reservation_manager.get_user_reservation(user_id)

    # ✅ Cancelar reservas
    elif any(phrase in incoming_msg for phrase in ["cancelar", "cancela", "anular", "eliminar reserva"]):
        response_text = reservation_manager.cancel_reservation(user_id)

    # ✅ Crear una nueva reserva
    elif "reservar" in incoming_msg or "quiero una mesa" in incoming_msg:
        response_text = reservation_manager.handle_reservation(user_id, incoming_msg)

    # ✅ Conversación con la IA
    else:
        response_text = chat_with_ai(incoming_msg, user_id)

    logging.debug(f"📤 Respuesta enviada a {user_id}: {response_text}")

    # Responder con Twilio
    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logging.info(f"🚀 Servidor iniciado en el puerto {port}")
    app.run(host="0.0.0.0", port=port)