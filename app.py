import logging
import re
import os
import psycopg2
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

# Cargar variables de entorno
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("❌ ERROR: La variable de entorno DATABASE_URL no está configurada.")

# Conectar a la base de datos
try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reservations (
            id SERIAL PRIMARY KEY,
            user_id TEXT,
            date TEXT,
            time TEXT,
            people INTEGER
        );
    ''')
    conn.commit()
    logging.info("✅ Tabla de reservas verificada/creada.")
except Exception as e:
    logging.error(f"❌ Error al conectar a la base de datos: {e}")
    raise

# Inicializar Flask
app = Flask(__name__)

@app.route("/")
def home():
    logging.debug("✅ Endpoint '/' ha sido accedido")
    return "✅ El bot está funcionando correctamente. Usa /whatsapp para interactuar."

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    """Maneja los mensajes de WhatsApp y gestiona reservas."""
    incoming_msg = request.values.get("Body", "").strip().lower()
    user_id = request.values.get("From", "")

    logging.debug(f"📩 Mensaje recibido de {user_id}: {incoming_msg}")

    # Intentar extraer detalles de la reserva con regex
    match = re.search(r"(\d{1,2} de \w+|mañana) a las (\d{1,2}:\d{2}) para (\d+) personas?", incoming_msg)
    
    if match:
        date, time, people = match.groups()
        logging.debug(f"📝 Datos extraídos: Fecha={date}, Hora={time}, Personas={people}")
        
        # Guardar en la base de datos
        try:
            cursor.execute(
                "INSERT INTO reservations (user_id, date, time, people) VALUES (%s, %s, %s, %s)",
                (user_id, date, time, int(people))
            )
            conn.commit()
            response_text = f"✅ ¡Reserva confirmada! Mesa para {people} personas el {date} a las {time}."
            logging.info(f"📌 Reserva guardada correctamente para {user_id}")
        except Exception as e:
            logging.error(f"❌ Error al guardar la reserva: {e}")
            response_text = "Lo siento, ha ocurrido un error al procesar tu reserva."
    else:
        response_text = "Por favor, dime la fecha y la hora exacta para la reserva."  

    # Responder con Twilio
    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logging.info(f"🚀 Servidor iniciado en el puerto {port}")
    app.run(host="0.0.0.0", port=port)