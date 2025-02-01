import re
from db import db
import logging

logging.basicConfig(level=logging.INFO)

class ReservationManager:
    def __init__(self):
        self.user_reservations = {}

    def extract_details(self, message):
        """Extrae la fecha, hora y número de personas de un mensaje de reserva."""
        date = re.search(r'(\d{1,2}/\d{1,2}|\d{1,2} de [a-zA-Z]+)', message)
        time = re.search(r'(\d{1,2}:\d{2}|\d{1,2} (?:AM|PM|am|pm))', message)
        people = re.search(r'(\d+)\s*(?:personas?|somos|para)', message)

        return (date.group(0) if date else None, 
                time.group(0) if time else None, 
                people.group(1) if people else None)

    def handle_reservation(self, user_id, message):
        """Gestiona el flujo de reservas y guarda en la base de datos."""
        logging.info(f"📩 Procesando reserva para {user_id}: {message}")

        if user_id not in self.user_reservations:
            self.user_reservations[user_id] = {"date": None, "time": None, "people": None}

        details = self.extract_details(message)
        keys = ["date", "time", "people"]
        
        for key, value in zip(keys, details):
            if value and not self.user_reservations[user_id][key]:
                self.user_reservations[user_id][key] = value

        reservation_data = self.user_reservations[user_id]

        if all(reservation_data.values()):
            db.add_reservation(user_id, reservation_data["date"], reservation_data["time"], reservation_data["people"])
            confirmation = f"✅ Reserva confirmada para {reservation_data['date']} "\
                           f"a las {reservation_data['time']} para "\
                           f"{reservation_data['people']} personas. ¡Gracias por reservar en *La Terraza*! 🍽️"
            del self.user_reservations[user_id]  # Elimina la reserva temporal
            return confirmation
        return "Necesito más detalles para completar la reserva."

    def get_user_reservation(self, user_id):
        """Consulta si el usuario tiene una reserva activa."""
        reserva = db.get_reservation(user_id)
        if reserva:
            return f"🔎 Tienes una reserva para el {reserva['date']} a las {reserva['time']} para {reserva['people']} personas."
        return "⚠️ No tienes ninguna reserva activa en este momento."

    def cancel_reservation(self, user_id):
        """Cancela una reserva del usuario."""
        db.delete_reservation(user_id)
        return "❌ Tu reserva ha sido cancelada correctamente."

# Instancia global del gestor de reservas
reservation_manager = ReservationManager()