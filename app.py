from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os
from bot import chat_with_ai
from reservations import reservation_manager

import logging
import sys

logging.info(f"📩 Mensaje recibido: {incoming_msg} de {user_id}")

# ✅ Habilitar logs en Render
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# ✅ Forzar que Flask muestre los `print()`
import os
if not os.getenv("FLASK_ENV"):  # Si no está en modo desarrollo
    import sys
    print = lambda *args, **kwargs: sys.stdout.write(" ".join(map(str, args)) + "\n")


# Cargar variables de entorno
load_dotenv()
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
    incoming_msg = request.values.get("Body", "").strip().lower()
    user_id = request.values.get("From", "")

    print(f"📩 Mensaje recibido: {incoming_msg} de {user_id}")  # DEBUG

    # ✅ Consultar reservas activas
    if "qué reservas tengo" in incoming_msg or "tengo alguna reserva" in incoming_msg:
        print("🔍 Se detectó consulta de reservas")  # DEBUG
        response_text = reservation_manager.get_user_reservation(user_id)
    
    # ✅ Cancelar reservas
    elif any(phrase in incoming_msg for phrase in ["cancelar", "cancela", "anular", "eliminar reserva"]):
        print("❌ Se detectó una cancelación de reserva")  # DEBUG
        response_text = reservation_manager.cancel_reservation(user_id)

    # ✅ Crear una nueva reserva
    elif "reservar" in incoming_msg or "quiero una mesa" in incoming_msg:
        print("📅 Se detectó una solicitud de reserva")  # DEBUG
        response_text = reservation_manager.handle_reservation(user_id, incoming_msg)

    # ✅ Conversación con la IA
    else:
        print("🤖 Se detectó una consulta general a la IA")  # DEBUG
        response_text = chat_with_ai(incoming_msg, user_id)

    # Responder con Twilio
    print(f"📤 Respuesta enviada: {response_text}")  # DEBUG
    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"🚀 Servidor iniciado en el puerto {port}")
    app.run(host="0.0.0.0", port=port, debug=True)