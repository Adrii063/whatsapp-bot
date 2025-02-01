import logging
import re
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os
from reservations import reservation_manager

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

# Cargar variables de entorno
load_dotenv()

# Inicializar Flask
app = Flask(__name__)

@app.route("/")
def home():
    logging.debug("✅ Endpoint '/' ha sido accedido")
    return "✅ El bot está funcionando correctamente. Usa /whatsapp para interactuar."

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    """Maneja los mensajes de WhatsApp y gestiona reservas"""
    incoming_msg = request.values.get("Body", "").strip().lower()
    user_id = request.values.get("From", "")

    logging.debug(f"📩 Mensaje recibido de {user_id}: {incoming_msg}")

    # Detectar si el mensaje es una solicitud de reserva
    match = re.search(r"(\d{1,2} de \w+|\bmañana\b) a las (\d{1,2}:\d{2}) para (\d+) personas?", incoming_msg)
    if match:
        date, time, people = match.groups()
        logging.debug(f"📝 Datos extraídos: Fecha={date}, Hora={time}, Personas={people}")

        try:
            reservation_manager.add_reservation(user_id, date, time, int(people))
            response_text = f"✅ ¡Reserva confirmada! Mesa para {people} personas el {date} a las {time}."
            logging.info(f"📌 Reserva guardada correctamente para {user_id}")
        except Exception as e:
            if "duplicate key value" in str(e):
                response_text = "❌ Ya tienes una reserva activa. ¿Quieres modificarla o cancelarla?"
            else:
                response_text = "❌ Error al procesar la reserva. Intenta de nuevo más tarde."
            logging.error(f"❌ Error al guardar la reserva: {e}")

    else:
        response_text = "No entendí tu solicitud. Por favor, indica la fecha, hora y número de personas."

    # Responder con Twilio
    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logging.info(f"🚀 Servidor iniciado en el puerto {port}")
    app.run(host="0.0.0.0", port=port)