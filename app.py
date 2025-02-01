import logging
import re
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os
from bot import chat_with_ai
from db import db  # Asegúrate de que `db.py` tenga la función correcta

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
    incoming_msg = request.values.get("Body", "").strip()
    user_id = request.values.get("From", "")

    logging.debug(f"📩 Mensaje recibido de {user_id}: {incoming_msg}")

    # Detectar si el mensaje es una solicitud de reserva
    if "reservar" in incoming_msg.lower() or "quiero una mesa" in incoming_msg.lower():
        match = re.search(r"(\d{1,2} de \w+|\bmañana\b) a las (\d{1,2}:\d{2}) para (\d+) personas?", incoming_msg)
        if match:
            date, time, people = match.groups()
            logging.debug(f"📝 Datos extraídos: Fecha={date}, Hora={time}, Personas={people}")

            # Preguntar por nombre y teléfono
            response_text = f"Para completar la reserva, dime tu nombre y número de contacto."
            user_data[user_id] = {"date": date, "time": time, "people": int(people)}
        
        else:
            response_text = "Por favor, dime la fecha y la hora exacta para la reserva."

    elif user_id in user_data:
        # Procesar segunda parte: recibir nombre y teléfono
        match = re.search(r"mi nombre es (\w+) y mi número de teléfono es (\d+)", incoming_msg, re.IGNORECASE)
        if match:
            name, phone = match.groups()
            reservation = user_data.pop(user_id)

            try:
                logging.debug("🔹 Verificando conexión a la base de datos...")
                db.check_connection()

                logging.debug(f"📝 Guardando reserva: {user_id}, {reservation['date']}, {reservation['time']}, {reservation['people']} personas.")
                db.add_reservation(user_id, reservation["date"], reservation["time"], reservation["people"])
                db.commit()  # Confirmar la transacción

                response_text = f"✅ ¡Reserva confirmada para {reservation['people']} personas el {reservation['date']} a las {reservation['time']}! 🎉"
                logging.info(f"📌 Reserva guardada correctamente para {user_id}")

            except Exception as e:
                logging.error(f"❌ Error al guardar la reserva: {e}")
                response_text = "Lo siento, ha ocurrido un error al procesar tu reserva."

        else:
            response_text = "Formato incorrecto. Envíame tu nombre y teléfono en este formato: 'Mi nombre es [nombre] y mi número de teléfono es [número]'."

    else:
        # Usar IA si no es una reserva
        response_text = chat_with_ai(incoming_msg, user_id)

    # Responder con Twilio
    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logging.info(f"🚀 Servidor iniciado en el puerto {port}")
    app.run(host="0.0.0.0", port=port)