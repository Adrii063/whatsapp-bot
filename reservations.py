from db import db

class ReservationManager:
    def get_user_reservation(self, user_id):
        reservation = db.get_reservation(user_id)
        if reservation:
            return f"📌 Tienes una reserva el {reservation['date']} a las {reservation['time']} para {reservation['people']} personas."
        return "⚠️ No tienes reservas activas en este momento."

    def cancel_reservation(self, user_id):
        db.delete_reservation(user_id)
        return "❌ Tu reserva ha sido cancelada correctamente."

    def handle_reservation(self, user_id, message):
        date, time, people = self.extract_details(message)
        
        if not all([date, time, people]):
            return "Por favor, dime la fecha, hora y número de personas para la reserva."

        db.add_reservation(user_id, date, time, people)
        return f"✅ Reserva confirmada para el {date} a las {time} para {people} personas."

    def extract_details(self, message):
        """Extrae los datos de una reserva desde un mensaje."""
        import re
        date = re.search(r'(\d{1,2}/\d{1,2}|\d{1,2} de [a-zA-Z]+)', message)
        time = re.search(r'(\d{1,2}:\d{2}|\d{1,2} (?:AM|PM|am|pm))', message)
        people = re.search(r'(\d+)\s*(?:personas?|somos|para)', message)

        return (date.group(0) if date else None, 
                time.group(0) if time else None, 
                people.group(1) if people else None)

reservation_manager = ReservationManager()