from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
import re
import os

# Configuración de OpenRouter con el modelo LFM-7B
api_key = os.getenv("OPENAI_API_KEY")
client = openai.OpenAI(api_key=api_key, base_url="https://openrouter.ai/api/v1")

app = Flask(__name__)

# Diccionarios para manejar múltiples usuarios
user_conversations = {}
user_reservations = {}

WELCOME_MESSAGE = "¡Hola! Soy el asistente virtual de *Restaurante La Terraza* 🍽️. "\
                  "Puedes preguntarme sobre el menú, reservar una mesa o conocer nuestros horarios."

def chat_with_ai(user_input, user_id):
    """Maneja la conversación personalizada para cada usuario"""
    if user_id not in user_conversations:
        user_conversations[user_id] = [
            {"role": "system", "content": "Eres un recepcionista del restaurante 'La Terraza'. "
                                          "Tu trabajo es ayudar con reservas, responder preguntas "
                                          "sobre el menú, horarios y cualquier otra duda."},
            {"role": "assistant", "content": WELCOME_MESSAGE}
        ]
    
    user_conversations[user_id].append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="openai/gpt-4o",
        messages=user_conversations[user_id],
        max_tokens=300,
        temperature=0.7
    )

    if response.choices and response.choices[0].message:
        bot_response = response.choices[0].message.content
        user_conversations[user_id].append({"role": "assistant", "content": bot_response})

        # 🔹 Bloquear respuestas que digan que no puede ver reservas
        if "no tengo acceso" in bot_response.lower() or "no puedo ver tus reservas" in bot_response.lower():
            return "Si deseas revisar tus reservas activas, dime '¿Tengo alguna reserva?' y te diré los detalles."

        return bot_response
    
    return "Lo siento, no tengo una respuesta en este momento. ¿Puedo ayudarte en algo más?"

def extract_reservation_details(message):
    """Extrae la fecha, hora y número de personas de un mensaje de reserva"""
    date_match = re.search(r'(\d{1,2}/\d{1,2})|(\d{1,2} de [a-zA-Z]+)', message)
    time_match = re.search(r'(\d{1,2}[:h]\d{2})|(\d{1,2} (?:AM|PM|am|pm))', message)
    people_match = re.search(r'(\d+)\s*(?:personas?|somos|para)', message)

    date_str = date_match.group(0) if date_match else None
    time_str = time_match.group(0) if time_match else None
    people_count = people_match.group(1) if people_match else None

    return date_str, time_str, people_count

def handle_reservation(user_input, user_id):
    """Gestiona reservas asegurando que cada usuario tenga su propia sesión"""
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
        return confirmation_msg
    
    return None

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    """Manejar mensajes de WhatsApp y detectar reservas y comandos automáticamente"""
    incoming_msg = request.values.get("Body", "").strip().lower()
    user_id = request.values.get("From", "")

    # ✅ Si el usuario pregunta por sus reservas activas
    if "qué reservas tengo" in incoming_msg or "tengo alguna reserva" in incoming_msg:
        if user_id in user_reservations and all(user_reservations[user_id].values()):
            res = user_reservations[user_id]
            response_text = f"Tienes una reserva para el {res['date']} a las {res['time']} para {res['people']} personas. 😊"
        else:
            response_text = "No tienes ninguna reserva activa en este momento."

        resp = MessagingResponse()
        resp.message(response_text)
        return str(resp)

    # ✅ Cancelar reserva
    cancel_phrases = ["cancelar", "cancela", "anular", "eliminar reserva", "borra la reserva"]
    if any(phrase in incoming_msg for phrase in cancel_phrases):
        if user_id in user_reservations:
            del user_reservations[user_id]
            response_text = "❌ Tu reserva ha sido cancelada correctamente."
        else:
            response_text = "⚠️ No tienes ninguna reserva activa para cancelar."
        
        resp = MessagingResponse()
        resp.message(response_text)
        return str(resp)

    # ✅ Hacer una nueva reserva
    if "reservar" in incoming_msg or "quiero una mesa" in incoming_msg:
        reservation_response = handle_reservation(incoming_msg, user_id)
        if reservation_response:
            response_text = reservation_response
        else:
            response_text = "¿Podrías darme más detalles sobre la reserva?"
        
        resp = MessagingResponse()
        resp.message(response_text)
        return str(resp)

    # ✅ Conversación normal con la IA
    response_text = chat_with_ai(incoming_msg, user_id)
    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render asigna un puerto dinámicamente
    app.run(host="0.0.0.0", port=port)