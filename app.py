import logging
import os
import re
import json
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
from reservations import reservation_manager

# Cargar variables de entorno
load_dotenv()
API_KEY = os.getenv("OPENAI_API_KEY")

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

# Inicializar Flask
app = Flask(__name__)

@app.route("/")
def home():
    logging.debug("✅ Endpoint '/' ha sido accedido")
    return "✅ El bot está funcionando correctamente."

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    """Maneja los mensajes de WhatsApp"""
    incoming_msg = request.values.get("Body", "").strip()
    user_id = request.values.get("From", "")

    logging.debug(f"📩 Mensaje recibido de {user_id}: {incoming_msg}")

    # Procesar la solicitud con IA
    reservation_data = extract_reservation_details(incoming_msg)

    if reservation_data:
        date, time, people = reservation_data["fecha"], reservation_data["hora"], reservation_data["personas"]

        if reservation_manager.add_reservation(user_id, date, time, people):
            response_text = f"✅ ¡Reserva confirmada! Mesa para {people} personas el {date} a las {time}."
        else:
            response_text = "❌ Error: No se pudo procesar la reserva."
    else:
        response_text = "No entendí tu solicitud. Por favor, dime la fecha, hora y número de personas."

    # Responder con Twilio
    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)

def extract_reservation_details(text):
    """Extrae la fecha, hora y número de personas usando OpenRouter"""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
    
    prompt = f"""
    Extrae la fecha, hora y número de personas de la siguiente solicitud de reserva:
    
    "{text}"
    
    Devuelve la respuesta en JSON con las claves "fecha", "hora" y "personas".
    """

    payload = {
        "model": "openai/gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 100,
        "temperature": 0.3
    }

    response = requests.post(url, headers=headers, json=payload)

    try:
        response_json = response.json()
        extracted_data = json.loads(response_json["choices"][0]["message"]["content"])
        logging.debug(f"📩 Respuesta de OpenRouter: {extracted_data}")
        return extracted_data
    except Exception as e:
        logging.error(f"❌ Error en la respuesta de OpenRouter: {e}")
        return None

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    logging.info(f"🚀 Servidor iniciado en el puerto {port}")
    app.run(host="0.0.0.0", port=port)