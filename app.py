from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv
import os
from bot import chat_with_ai
from reservations import handle_reservation, user_reservations

# Cargar variables de entorno desde .env
load_dotenv()

# Configurar API key de OpenAI
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ ERROR: La variable de entorno OPENAI_API_KEY no está configurada.")

# Inicializar Flask
app = Flask(__name__)

@app.route("/")
def home():
    return "✅ El bot está funcionando correctamente. Usa /whatsapp para interactuar."

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    """Maneja los mensajes de WhatsApp y gestiona reservas y preguntas con IA"""
    incoming_msg = request.values.get("Body", "").strip().lower()
    user_id = request.values.get("From", "")

    # ✅ Consultar reservas activas
    if "qué reservas tengo" in incoming_msg or "tengo alguna reserva" in incoming_msg:
        if user_id in user_reservations and all(user_reservations[user_id].values()):
            res = user_reservations[user_id]
            response_text = f"Tienes una reserva para el {res['date']} a las {res['time']} para {res['people']} personas. 😊"
        else:
            response_text = "No tienes ninguna reserva activa en este momento."

        resp = MessagingResponse()
        resp.message(response_text)
        return str(resp)

    # ✅ Cancelar reservas
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

    # ✅ Crear una nueva reserva
    if "reservar" in incoming_msg or "quiero una mesa" in incoming_msg:
        reservation_response = handle_reservation(incoming_msg, user_id)
        if reservation_response:
            response_text = reservation_response
        else:
            response_text = "¿Podrías darme más detalles sobre la reserva?"
        
        resp = MessagingResponse()
        resp.message(response_text)
        return str(resp)

    # ✅ Conversación con la IA
    response_text = chat_with_ai(incoming_msg, user_id)
    resp = MessagingResponse()
    resp.message(response_text)
    return str(resp)

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))  # Render asigna un puerto dinámicamente
    print(f"🚀 Servidor iniciado en el puerto {port}")
    app.run(host="0.0.0.0", port=port)