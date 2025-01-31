from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
import re  # Librería para detectar comandos con expresiones regulares
from datetime import datetime
import os
# Configuración de OpenRouter con el modelo LFM-7B

# Imprimir API Key para verificar si se está pasando correctamente
api_key = os.getenv("OPENAI_API_KEY")
print(f"🔍 OPENAI_API_KEY: {api_key}")

client = openai.OpenAI(
    api_key=api_key,
    base_url="https://openrouter.ai/api/v1"
)

app = Flask(__name__)
@app.route("/")
def home():
    return "¡El bot está funcionando! Usa /whatsapp para interactuar."

# Diccionario para almacenar el historial de conversaciones y reservas
user_conversations = {}
user_reservations = {}

WELCOME_MESSAGE = "¡Hola! Soy el asistente virtual de *Restaurante La Terraza* 🍽️. "\
                  "Puedes preguntarme sobre el menú, reservar una mesa o conocer nuestros horarios."

def chat_with_ai(user_input, user_id):
    """Función para obtener una respuesta de LFM-7B con memoria y lógica de recepcionista"""
    try:
        if user_id not in user_conversations:
            user_conversations[user_id] = [
                {"role": "system", "content": "Eres un recepcionista del restaurante 'La Terraza'. "
                                                 "Responde de manera corta y precisa, no más de 2 frases. "
                                                 "Tu trabajo es ayudar con reservas, responder preguntas "
                                                 "sobre el menú, horarios y cualquier otra duda."},
                {"role": "assistant", "content": WELCOME_MESSAGE}
            ]
        
        user_conversations[user_id].append({"role": "user", "content": user_input})

        response = client.chat.completions.create(
            model="liquid/lfm-7b",
            messages=user_conversations[user_id],
            max_tokens=300,
            temperature=0.7
        )

        if response.choices and response.choices[0].message:
            bot_response = response.choices[0].message.content
            user_conversations[user_id].append({"role": "assistant", "content": bot_response})
            return bot_response
        
        return "Lo siento, no tengo una respuesta en este momento. ¿Puedo ayudarte en algo más?"
    
    except Exception as e:
        return f"Error al procesar la solicitud: {str(e)}"

def extract_reservation_details(message):
    """Extrae la fecha, hora y número de personas de un mensaje de reserva"""
    try:
        date_match = re.search(r'(\d{1,2}/\d{1,2})|(\d{1,2} de [a-zA-Z]+)', message)
        time_match = re.search(r'(\d{1,2}[:h]\d{2})|(\d{1,2} (?:AM|PM|am|pm))', message)
        people_match = re.search(r'(\d+)\s*(?:personas?|somos|para)', message)

        date_str = date_match.group(0) if date_match else None
        time_str = time_match.group(0) if time_match else None
        people_count = people_match.group(1) if people_match else None

        return date_str, time_str, people_count
    except Exception:
        return None, None, None

def handle_reservation(user_input, user_id):
    """Maneja el flujo de reservas asegurando que se recopilen todos los datos antes de confirmar."""
    if user_id not in user_reservations:
        user_reservations[user_id] = {"date": None, "time": None, "people": None}

    reservation_data = user_reservations[user_id]
    date, time, people = extract_reservation_details(user_input)

    if date and reservation_data["date"] is None:
        reservation_data["date"] = date
        return "Gracias. Ahora dime, ¿a qué hora te gustaría reservar?"

    if time and reservation_data["time"] is None:
        reservation_data["time"] = time

    if reservation_data["time"] and reservation_data["people"] is None:
        return "Perfecto. ¿Para cuántas personas será la reserva?"

    if people and reservation_data["people"] is None:
        reservation_data["people"] = people

    if reservation_data["date"] and reservation_data["time"] and reservation_data["people"]:
        confirmation_msg = f"✅ Reserva confirmada para el {reservation_data['date']} "\
                           f"a las {reservation_data['time']} para {reservation_data['people']} personas. "\
                           f"¡Te esperamos en *La Terraza*! 🎉"
        user_reservations.pop(user_id, None)
        return confirmation_msg
    
    return None

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    """Manejar mensajes de WhatsApp y detectar reservas y comandos automáticamente"""
    incoming_msg = request.values.get("Body", "").strip()
    user_id = request.values.get("From", "")

    cancel_phrases = ["cancelar", "cancela", "anular", "eliminar reserva", "borra la reserva"]
    if any(phrase in incoming_msg.lower() for phrase in cancel_phrases):
        if user_id in user_reservations:
            del user_reservations[user_id]
            response_text = "❌ Tu reserva ha sido cancelada correctamente."
        else:
            response_text = "⚠️ No tienes ninguna reserva activa para cancelar."
        resp = MessagingResponse()
        resp.message(response_text)
        return str(resp)

    if "reservar" in incoming_msg.lower() or "quiero una mesa" in incoming_msg.lower():
        reservation_response = handle_reservation(incoming_msg, user_id)
        if reservation_response:
            response_text = reservation_response
        else:
            response_text = "¿Podrías darme más detalles sobre la reserva?"
        resp = MessagingResponse()
        resp.message(response_text)
        return str(resp)

    response_text = chat_with_ai(incoming_msg, user_id)
    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render asigna un puerto dinámicamente
    app.run(host="0.0.0.0", port=port)