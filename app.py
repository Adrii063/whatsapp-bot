import logging
import re
import json
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os
import openai
from reservations import reservation_manager

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

# Cargar variables de entorno
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = api_key

# Inicializar Flask
app = Flask(__name__)

def extract_reservation_details(incoming_msg):
    """Usa GPT para estructurar la información de una reserva"""
    prompt = f"""
    Eres un asistente que extrae detalles de reservas en un restaurante.
    Extrae los siguientes datos del mensaje y devuélvelos en formato JSON:
    - Fecha de la reserva
    - Hora
    - Número de personas

    Si algún dato no está presente, usa `null`.  
    Mensaje: "{incoming_msg}"
    """

    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": "Eres un asistente experto en estructurar reservas de restaurantes."},
                  {"role": "user", "content": prompt}],
        max_tokens=100
    )

    structured_data = json.loads(response["choices"][0]["message"]["content"])
    return structured_data

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

    # Usar IA para extraer datos de reserva
    reservation_data = extract_reservation_details(incoming_msg)

    if reservation_data["fecha"] and reservation_data["hora"] and reservation_data["personas"]:
        date = reservation_data["fecha"]
        time = reservation_data["hora"]
        people = reservation_data["personas"]

        logging.debug(f"📝 Datos extraídos por IA: Fecha={date}, Hora={time}, Personas={people}")

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
        response_text = "No entendí tu solicitud. Por favor, dime la fecha, hora y número de personas."

    # Responder con Twilio
    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logging.info(f"🚀 Servidor iniciado en el puerto {port}")
    app.run(host="0.0.0.0", port=port)
