import logging
import re
import json
import os
import requests
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
from reservations import reservation_manager

# Configurar logging
logging.basicConfig(level=logging.DEBUG)

# Cargar variables de entorno
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")  # SE MANTIENE IGUAL

# Inicializar Flask
app = Flask(__name__)

def extract_reservation_details(incoming_msg):
    """Utiliza OpenRouter GPT-4o para extraer detalles de la reserva en JSON."""
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    prompt = f"""
    Eres un asistente para extraer datos de reservas de restaurante.
    Extrae los siguientes detalles del mensaje y devuelve un JSON válido con los campos:
    - fecha
    - hora
    - personas

    Si no encuentra alguno de estos datos, usa `null`.

    Mensaje: "{incoming_msg}"
    """
    data = {
        "model": "openai/gpt-4o",
        "messages": [{"role": "system", "content": "Eres un asistente que extrae datos de reservas."},
                     {"role": "user", "content": prompt}],
        "max_tokens": 100
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Lanza un error si la solicitud no es exitosa
        response_json = response.json()

        # Verifica si la respuesta contiene "choices" y extrae el JSON generado por la IA
        if "choices" in response_json and response_json["choices"]:
            message_content = response_json["choices"][0]["message"]["content"].strip()
            logging.debug(f"📩 Respuesta de OpenRouter antes de limpiar: {message_content}")

            # Eliminar posibles etiquetas de bloque de código (```json ... ```)
            cleaned_content = re.sub(r"```json\n(.*?)\n```", r"\1", message_content, flags=re.DOTALL).strip()

            # Intentar convertir la respuesta a JSON
            try:
                structured_data = json.loads(cleaned_content)
                return structured_data
            except json.JSONDecodeError:
                logging.error("❌ Error en la respuesta de OpenRouter: No es JSON válido.")
                return {"fecha": None, "hora": None, "personas": None}
        else:
            logging.error("❌ Respuesta de OpenRouter vacía o inesperada.")
            return {"fecha": None, "hora": None, "personas": None}
    except requests.exceptions.RequestException as e:
        logging.error(f"❌ Error en la API de OpenRouter: {e}")
        return {"fecha": None, "hora": None, "personas": None}

@app.route("/")
def home():
    logging.debug("✅ Endpoint '/' ha sido accedido")
    return "✅ El bot está funcionando correctamente. Usa /whatsapp para interactuar."

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    """Maneja los mensajes de WhatsApp y gestiona reservas"""
    incoming_msg = request.values.get("Body", "").strip()
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