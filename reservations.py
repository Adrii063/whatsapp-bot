import re
import logging
from db import db

logging.basicConfig(level=logging.INFO)

class ReservationManager:
    def extract_details(self, message):
        """
        Extrae la fecha, hora y número de personas de un mensaje de reserva.
        """
        date_match = re.search(r'(\d{1,2}/\d{1,2}|\d{1,2} de [a-zA-Z]+)', message)
        time_match = re.search(r'(\d{1,2}[:h]\d{2}|\d{1,2} (?:AM|PM|am|pm))', message)
        people_match = re.search(r'(\d+)\s*(?:personas?|somos|para)', message)
        
        date_str = date_match.group(0) if date_match else None
        time_str = time_match.group(0) if time_match else None
        people_count = int(people_match.group(1)) if people_match else None

        return date_str, time_str, people_count

    def handle_reservation(self, user_id, message):
        """
        Procesa una reserva y la almacena en la base de datos.
        """
        logging.info(f"📩 Procesando reserva para {user_id}: {message}")

        # Extraer detalles
        date, time, people = self.extract_details(message)
        if not date or not time or not people:
            return "⚠️ Necesito que me indiques la fecha, la hora y cuántas personas asistirán."

        # Guardar reserva en la base de datos
        logging.info(f"📝 Guardando reserva: {user_id} - {date} - {time} - {people}")
        db.add_reservation(user_id, date, time, people)

        return f"✅ ¡Reserva confirmada! 🎉 Para {people} personas el {date} a las {time}. ¡Nos vemos en La Terraza!"

    def get_user_reservation(self, user_id):
        """
        Recupera una reserva específica de la base de datos.
        """
        reservation = db.get_reservation(user_id)
        if reservation:
            return f"📌 Tu reserva: {reservation['people']} personas el {reservation['date']} a las {reservation['time']}."
        return "⚠️ No tienes ninguna reserva activa."

    def cancel_reservation(self, user_id):
        """
        Cancela una reserva existente.
        """
        reservation = db.get_reservation(user_id)
        if reservation:
            db.delete_reservation(user_id)
            return "❌ Tu reserva ha sido cancelada correctamente."
        return "⚠️ No tienes ninguna reserva activa para cancelar."

# Instancia del gestor de reservas
reservation_manager = ReservationManager()