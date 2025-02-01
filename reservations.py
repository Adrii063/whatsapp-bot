import logging
import re
from db import db

class ReservationManager:
    def __init__(self):
        logging.info("🔹 Inicializando gestor de reservas")

    def extract_details(self, message):
        logging.info(f"🔍 Intentando extraer datos de la reserva: {message}")
        date = re.search(r'(\d{1,2}/\d{1,2}|\d{1,2} de [a-zA-Z]+)', message)
        time = re.search(r'(\d{1,2}:\d{2}|\d{1,2} (?:AM|PM|am|pm))', message)
        people = re.search(r'(\d+)\s*(?:personas?|somos|para)', message)

        return (date.group(0) if date else None, 
                time.group(0) if time else None, 
                people.group(1) if people else None)

    def handle_reservation(self, user_id, message):
        logging.info(f"📝 Procesando reserva para {user_id}: {message}")

        details = self.extract_details(message)
        if not all(details):
            return "Necesito que me indiques la fecha, hora y número de personas para la reserva."

        date, time, people = details
        logging.info(f"✅ Datos extraídos: Fecha {date}, Hora {time}, Personas {people}")

        db.add_reservation(user_id, date, time, people)
        return f"✅ Tu reserva ha sido confirmada para el {date} a las {time} para {people} personas."

    def get_user_reservation(self, user_id):
        reserva = db.get_reservation(user_id)
        if reserva:
            return f"Tienes una reserva para el {reserva['date']} a las {reserva['time']} para {reserva['people']} personas."
        return "No tienes ninguna reserva activa."

    def cancel_reservation(self, user_id):
        db.delete_reservation(user_id)
        return "❌ Tu reserva ha sido cancelada."

reservation_manager = ReservationManager()