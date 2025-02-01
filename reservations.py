import logging
import re
from db import db

logging.basicConfig(level=logging.INFO)

class ReservationManager:
    def __init__(self):
        pass

    def extract_reservation_details(self, message):
        """Extrae la fecha, hora y número de personas de un mensaje de reserva."""
        date_match = re.search(r'(\d{1,2}/\d{1,2}|\d{1,2} de [a-zA-Z]+)', message)
        time_match = re.search(r'(\d{1,2}:\d{2}|\d{1,2} (?:AM|PM|am|pm))', message)
        people_match = re.search(r'(\d+)\s*(?:personas?|somos|para)', message)

        date_str = date_match.group(0) if date_match else None
        time_str = time_match.group(0) if time_match else None
        people_count = int(people_match.group(1)) if people_match else None

        return date_str, time_str, people_count

    def handle_reservation(self, user_id, message):
        """Gestiona reservas asegurando que se guarden correctamente en la base de datos."""
        logging.info(f"📥 Recibida solicitud de reserva: {message} (de {user_id})")

        date, time, people = self.extract_reservation_details(message)

        if not date or not time or not people:
            logging.warning("⚠️ No se pudieron extraer todos los datos de la reserva.")
            return "Por favor, proporciona la fecha, hora y número de personas para la reserva."

        logging.info(f"📝 Datos extraídos: Fecha: {date}, Hora: {time}, Personas: {people}")

        try:
            db.add_reservation(user_id, date, time, people)
            logging.info(f"✅ Reserva guardada para {user_id}: {date} {time}, {people} personas")
            return f"¡Listo! He reservado para {people} personas el {date} a las {time}."
        except Exception as e:
            logging.error(f"❌ Error al guardar la reserva en la BD: {e}")
            return "Hubo un error al procesar tu reserva. Inténtalo de nuevo."

    def get_user_reservation(self, user_id):
        """Recupera una reserva existente para un usuario."""
        logging.info(f"🔍 Buscando reserva para {user_id} en la base de datos...")
        reservation = db.get_reservation(user_id)

        if reservation:
            logging.info(f"✅ Reserva encontrada: {reservation}")
            return f"Tienes una reserva para el {reservation['date']} a las {reservation['time']} para {reservation['people']} personas."
        else:
            logging.info("⚠️ No se encontró ninguna reserva activa para este usuario.")
            return "No tienes ninguna reserva activa en este momento."

    def cancel_reservation(self, user_id):
        """Elimina la reserva de un usuario si existe."""
        logging.info(f"🗑 Intentando cancelar la reserva de {user_id}...")
        reservation = db.get_reservation(user_id)

        if reservation:
            db.delete_reservation(user_id)
            logging.info(f"✅ Reserva eliminada con éxito para {user_id}")
            return "Tu reserva ha sido cancelada correctamente."
        else:
            logging.warning("⚠️ No se encontró ninguna reserva para cancelar.")
            return "No tienes ninguna reserva activa para cancelar."

# Instancia global del gestor de reservas
reservation_manager = ReservationManager()