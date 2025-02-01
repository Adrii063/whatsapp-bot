import logging
import os
import re
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
from bot import chat_with_ai
from reservations import reservation_manager
from db import db  # Importamos la base de datos

# Configurar logging para depuración
logging.basicConfig(level=logging.DEBUG)

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

    # Detectar si el mensaje es una solicitud de reserva
    match = re.search(r"(\d{1,2} de \w+|\bmañana\b) a las (\d{1,2}:\d{2}) para (\d+) personas?", incoming_msg)
    
    if match:
        date, time, people = match.groups()
        people = int(people)

        logging.debug(f"📝 Datos extraídos: Fecha={date}, Hora={time}, Personas={people}")

        # Verificar si el usuario ya proporcionó su nombre y teléfono
        if "nombre" not in incoming_msg and "teléfono" not in incoming_msg:
            response_text = "Para completar la reserva, dime tu nombre y número de contacto."
            return send_whatsapp_response(response_text)

    # Detectar si el usuario envió su nombre y teléfono
    match_contact = re.search(r"mi nombre es ([a-zA-Z]+) y mi número de teléfono es (\d+)", incoming_msg)
    if match_contact:
        name, phone = match_contact.groups()

        logging.debug(f"📇 Datos de contacto: Nombre={name}, Teléfono={phone}")

        try:
            db.add_reservation(user_id, date, time, people)
            response_text = f"✅ ¡Reserva confirmada! {name}, tu mesa para {people} personas el {date} a las {time} ha sido guardada. Si necesitas hacer algún cambio, avísame."
            logging.info(f"📌 Reserva guardada correctamente para {user_id}")
        except Exception as e:
            logging.error(f"❌ Error al guardar la reserva: {e}")
            response_text = "Lo siento, ha ocurrido un error al procesar tu reserva."

        return send_whatsapp_response(response_text)

    # Si el mensaje no es de reserva, usar IA
    response_text = chat_with_ai(incoming_msg, user_id)
    return send_whatsapp_response(response_text)

def send_whatsapp_response(message):
    """Envía una respuesta formateada a WhatsApp con Twilio"""
    resp = MessagingResponse()
    resp.message(message)
    return str(resp)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logging.info(f"🚀 Servidor iniciado en el puerto {port}")
    app.run(host="0.0.0.0", port=port)