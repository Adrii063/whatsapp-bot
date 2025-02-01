import logging
import re
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os
from bot import chat_with_ai
from reservations import reservation_manager
from db import db

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

    # ✅ Detectar si el mensaje es una solicitud de reserva
    if "reservar" in incoming_msg or "quiero una mesa" in incoming_msg:
        match = re.search(r"(\d{1,2} de \w+|\bmañana\b) a las (\d{1,2}:\d{2}) para (\d+) personas?", incoming_msg)
        if match:
            date, time, people = match.groups()
            logging.debug(f"📝 Datos extraídos: Fecha={date}, Hora={time}, Personas={people}")

            try:
                # **Verificar conexión antes de insertar**
                logging.debug("🔹 Verificando conexión a la base de datos...")
                db.check_connection()

                # **Guardar reserva en la base de datos**
                logging.debug(f"📝 Intentando guardar reserva: {user_id}, {date}, {time}, {people} personas.")
                db.add_reservation(user_id, date, time, int(people))
                db.commit()  # **Importante: Confirmar la transacción**
                
                response_text = f"✅ ¡Reserva confirmada! Mesa para {people} personas el {date} a las {time}."
                logging.info(f"📌 Reserva guardada correctamente para {user_id}")
            except Exception as e:
                logging.error(f"❌ Error al guardar la reserva: {e}")
                response_text = "Lo siento, ha ocurrido un error al procesar tu reserva."

        else:
            response_text = "Por favor, dime la fecha y la hora exacta para la reserva."

    # ✅ Si no es una reserva, usar IA
    else:
        response_text = chat_with_ai(incoming_msg, user_id)

    # Responder con Twilio
    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logging.info(f"🚀 Servidor iniciado en el puerto {port}")
    app.run(host="0.0.0.0", port=port)