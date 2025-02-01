from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os
import logging
from bot import chat_with_ai
from reservations import reservation_manager

# Cargar variables de entorno
load_dotenv()

# Configurar logs
logging.basicConfig(level=logging.INFO)

# Verificar que `DATABASE_URL` está definida
database_url = os.getenv("DATABASE_URL")
if not database_url:
    raise ValueError("❌ ERROR: La variable de entorno DATABASE_URL no está configurada correctamente.")

# Inicializar Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ El bot está funcionando correctamente. Usa /whatsapp para interactuar."

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    """Maneja los mensajes de WhatsApp y gestiona reservas y preguntas con IA"""
    incoming_msg = request.values.get("Body", "").strip().lower()
    user_id = request.values.get("From", "")

    logging.info(f"📩 Mensaje recibido de {user_id}: {incoming_msg}")

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

    # Responder con Twilio
    logging.info(f"📤 Respuesta enviada a {user_id}: {response_text}")
    
    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logging.info(f"🚀 Servidor iniciado en el puerto {port}")
    app.run(host="0.0.0.0", port=port)