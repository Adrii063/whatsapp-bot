import logging
import re
from db import db

class ReservationManager:
    def __init__(self):
        logging.info("📌 Módulo de reservas cargado correctamente.")

    def extract_details(self, message):
        """Extrae la fecha, hora y número de personas de un mensaje de reserva."""
        date_match = re.search(r'(\d{1,2}/\d{1,2}|\d{1,2} de [a-zA-Z]+)', message)
        time_match = re.search(r'(\d{1,2}:\d{2}|\d{1,2} (?:AM|PM|am|pm))', message)
        people_match = re.search(r'(\d+)\s*(?:personas?|somos|para)', message)

        date_str = date_match.group(0) if date_match else None
        time_str = time_match.group(0) if time_match else None
        people_count = int(people_match.group(1)) if people_match else None

        return date_str, time_str, people_count

    def handle_reservation(self, user_id, message):
        """Gestiona la reserva de un usuario."""
        logging.info(f"🟡 Recibida solicitud de reserva de {user_id}: {message}")

        date, time, people = self.extract_details(message)
        if not (date and time and people):
            logging.warning(f"⚠️ No se pudieron extraer todos los detalles de la reserva de {user_id}.")
            return "Por favor, proporciona la fecha, hora y cantidad de personas para la reserva."

        logging.info(f"✅ Datos extraídos: {date}, {time}, {people} personas.")

        # 🔹 Intenta guardar la reserva en la base de datos
        try:
            db.add_reservation(user_id, date, time, people)
            logging.info(f"📝 Intentando agregar reserva para {user_id}: {date} {time}, {people} personas")
        except Exception as e:
            logging.error(f"❌ Error al guardar la reserva en la base de datos: {e}")
            return "Hubo un problema al guardar tu reserva. Por favor, intenta nuevamente más tarde."

        return f"¡Listo! La reserva está confirmada para el {date} a las {time} para {people} personas."

reservation_manager = ReservationManager()