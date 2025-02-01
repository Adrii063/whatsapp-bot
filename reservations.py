from db import db

class ReservationManager:
    def handle_reservation(self, user_id, message):
        print(f"📥 handle_reservation() fue llamado para: {user_id} con mensaje: {message}")  # DEBUG
        """Gestiona la creación de reservas en la base de datos."""
        print(f"📥 Procesando reserva para {user_id}: {message}")  # DEBUG

        # Simulación de extracción de datos
        date, time, people = self.extract_details(message)

        if not date or not time or not people:
            return "Por favor, dime la fecha, la hora y cuántas personas asistirán para hacer la reserva."

        # Intenta guardar la reserva en la base de datos
        db.add_reservation(user_id, date, time, people)

        print(f"✅ Reserva guardada: {user_id}, {date}, {time}, {people}")  # DEBUG

        return f"Tu reserva para {people} personas el {date} a las {time} ha sido confirmada. 🎉"

    def extract_details(self, message):
        """Extrae detalles de la reserva desde el mensaje."""
        import re
        date_match = re.search(r'(\d{1,2}/\d{1,2}|\d{1,2} de [a-zA-Z]+)', message)
        time_match = re.search(r'(\d{1,2}:\d{2}|\d{1,2} (?:AM|PM|am|pm))', message)
        people_match = re.search(r'(\d+)\s*(?:personas?|somos|para)', message)

        date_str = date_match.group(0) if date_match else None
        time_str = time_match.group(0) if time_match else None
        people_count = people_match.group(1) if people_match else None

        return date_str, time_str, people_count

reservation_manager = ReservationManager()