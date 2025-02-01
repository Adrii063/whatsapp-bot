from db import db

class ReservationManager:
    def handle_reservation(self, user_id, message):
        """Procesa una nueva reserva basada en el mensaje del usuario."""
        date, time, people = self.extract_details(message)

        if not date or not time or not people:
            return "Necesito más detalles para completar la reserva (fecha, hora y número de personas)."

        db.add_reservation(user_id, date, time, people)
        return f"✅ Reserva confirmada para el {date} a las {time} para {people} personas."

    def get_user_reservation(self, user_id):
        """Obtiene la reserva de un usuario."""
        reservation = db.get_reservation(user_id)
        if reservation:
            return f"Tienes una reserva para el {reservation['date']} a las {reservation['time']} para {reservation['people']} personas. 😊"
        return "No tienes ninguna reserva activa en este momento."

    def cancel_reservation(self, user_id):
        """Cancela la reserva de un usuario."""
        reservation = db.get_reservation(user_id)
        if reservation:
            db.delete_reservation(user_id)
            return "❌ Tu reserva ha sido cancelada correctamente."
        return "⚠️ No tienes ninguna reserva activa para cancelar."

    def extract_details(self, message):
        """Extrae la fecha, hora y número de personas de un mensaje de reserva."""
        import re
        date_match = re.search(r'(\d{1,2}/\d{1,2})|(\d{1,2} de [a-zA-Z]+)', message)
        time_match = re.search(r'(\d{1,2}[:h]\d{2})|(\d{1,2} (?:AM|PM|am|pm))', message)
        people_match = re.search(r'(\d+)\s*(?:personas?|somos|para)', message)

        date_str = date_match.group(0) if date_match else None
        time_str = time_match.group(0) if time_match else None
        people_count = people_match.group(1) if people_match else None

        return date_str, time_str, people_count

# Instancia global del gestor de reservas
reservation_manager = ReservationManager()