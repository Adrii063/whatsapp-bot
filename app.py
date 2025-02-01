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

    # Inicializar variables de la reserva
    date, time, people = None, None, None
    
    # ✅ Detectar si el mensaje es una solicitud de reserva
    if "reservar" in incoming_msg or "quiero una mesa" in incoming_msg:
        match = re.search(r"(\d{1,2} de \w+|\bmañana\b) a las (\d{1,2}:\d{2}) para (\d+) personas?", incoming_msg)
        
        if match:
            date, time, people = match.groups()
            logging.debug(f"📝 Datos extraídos: Fecha={date}, Hora={time}, Personas={people}")
        else:
            logging.error("⚠️ No se pudo extraer la fecha, hora o número de personas correctamente.")
            response_text = "Por favor, dime la fecha y la hora exacta para la reserva."
            resp = MessagingResponse()
            resp.message(response_text)
            return str(resp)

        # Verificar que las variables sean válidas antes de guardar la reserva
        try:
            if not all([date, time, people]):
                raise ValueError("🚨 Error: Uno de los valores (fecha, hora, personas) está vacío.")
            
            logging.debug(f"🔍 Intentando guardar reserva: Usuario={user_id}, Fecha={date}, Hora={time}, Personas={people}")
            
            db.add_reservation(user_id, date, time, int(people))
            
            response_text = f"✅ ¡Reserva confirmada! Tu mesa para {people} personas el {date} a las {time} ha sido guardada."
            logging.info(f"📌 Reserva guardada correctamente para {user_id}")

        except Exception as e:
            logging.error(f"❌ ERROR AL GUARDAR RESERVA: {e}")
            response_text = f"⚠️ Ha ocurrido un error al guardar la reserva: {e}"
    
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