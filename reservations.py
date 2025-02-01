import re
from db import db

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
        """Procesa una solicitud de reserva y la almacena en la base de datos."""
        date, time, people = self.extract_details(message)

        if date and time and people:
            print(f"🔍 Datos extraídos para reserva: Fecha={date}, Hora={time}, Personas={people}")  # 🔍 Debug
            db.add_reservation(user_id, date, time, people)
            return f"✅ ¡Reserva confirmada! 📅 {date} 🕛 {time} para {people} personas."
        
        return "❌ Por favor, proporciona la fecha, la hora y el número de personas para la reserva."

    def get_user_reservation(self, user_id):
        """Recupera la reserva de un usuario si existe."""
        reservation = db.get_reservation(user_id)
        if reservation:
            return f"📅 Tienes una reserva para {reservation['date']} a las {reservation['time']} para {reservation['people']} personas."
        return "⚠️ No tienes ninguna reserva activa."

    def cancel_reservation(self, user_id):
        """Elimina la reserva de un usuario."""
        db.delete_reservation(user_id)
        return "❌ Tu reserva ha sido cancelada correctamente."

# Instancia global del manejador de reservas
reservation_manager = ReservationManager()