import logging
from db import db
import re

class ReservationManager:
    def __init__(self):
        logging.debug("🔹 Manejador de reservas inicializado")

    def extract_details(self, message):
        """Extrae la fecha, hora y número de personas de un mensaje de reserva"""
        date = re.search(r'(\d{1,2}/\d{1,2}|\d{1,2} de [a-zA-Z]+)', message)
        time = re.search(r'(\d{1,2}:\d{2}|\d{1,2} (?:AM|PM|am|pm))', message)
        people = re.search(r'(\d+)\s*(?:personas?|somos|para)', message)

        extracted = (
            date.group(0) if date else None, 
            time.group(0) if time else None, 
            people.group(1) if people else None
        )
        
        logging.debug(f"🔍 Datos extraídos del mensaje: {extracted}")
        return extracted

    def handle_reservation(self, user_id, message):
        """Gestiona la reserva de un usuario"""
        logging.debug(f"📝 Intentando procesar reserva para {user_id}")

        details = self.extract_details(message)
        if not all(details):
            return "Necesito más información. Por favor, dime la fecha, hora y número de personas para la reserva."

        date, time, people = details
        db.add_reservation(user_id, date, time, int(people))
        logging.debug(f"✅ Reserva guardada: {user_id} - {date}, {time}, {people} personas")

        return f"✅ Tu reserva para {people} personas el {date} a las {time} ha sido confirmada."

    def get_user_reservation(self, user_id):
        """Obtiene la reserva de un usuario"""
        logging.debug(f"🔍 Buscando reserva para {user_id}")
        reservation = db.get_reservation(user_id)

        if reservation:
            logging.debug(f"📌 Reserva encontrada: {reservation}")
            return f"Tienes una reserva para {reservation['people']} personas el {reservation['date']} a las {reservation['time']}."
        else:
            return "No tienes ninguna reserva activa."

    def cancel_reservation(self, user_id):
        """Cancela la reserva de un usuario"""
        logging.debug(f"❌ Intentando cancelar reserva para {user_id}")
        db.delete_reservation(user_id)
        return "Tu reserva ha sido cancelada con éxito."

reservation_manager = ReservationManager()