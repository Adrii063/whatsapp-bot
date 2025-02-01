import logging

logging.basicConfig(level=logging.DEBUG)

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    """Maneja los mensajes de WhatsApp y gestiona reservas y preguntas con IA"""
    incoming_msg = request.values.get("Body", "").strip().lower()
    user_id = request.values.get("From", "")

    logging.debug(f"📩 Mensaje recibido de {user_id}: {incoming_msg}")

    # Responder con Twilio
    resp = MessagingResponse()
    
    if "reservar" in incoming_msg or "mesa" in incoming_msg:
        logging.debug(f"🔍 Detectada intención de reserva en mensaje: {incoming_msg}")
        response_text = reservation_manager.handle_reservation(user_id, incoming_msg)
    else:
        response_text = chat_with_ai(incoming_msg, user_id)
    
    logging.debug(f"📤 Respuesta enviada a {user_id}: {response_text}")
    resp.message(response_text)
    return str(resp)