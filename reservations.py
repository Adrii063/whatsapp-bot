import re
from datetime import datetime, timedelta

class ReservationManager:
    def __init__(self):
        self.user_reservations = {}

    def extract_details(self, message):
        """Extrae la fecha, hora y número de personas de un mensaje de reserva"""
        today = datetime.today()
        date_match = re.search(r'(\d{1,2}/\d{1,2})|(\d{1,2} de [a-zA-Z]+)|mañana|pasado mañana', message.lower())
        time_match = re.search(r'(\d{1,2}:\d{2}|\d{1,2} (?:AM|PM|am|pm))', message)
        people_match = re.search(r'(\d+)\s*(?:personas?|somos|para)', message)

        date_str = date_match.group(0) if date_match else None
        time_str = time_match.group(0) if time_match else None
        people_count = people_match.group(1) if people_match else None

        # Manejo de fechas naturales
        if date_str:
            if "mañana" in date_str:
                date_str = (today + timedelta(days=1)).strftime("%d/%m")
            elif "pasado mañana" in date_str:
                date_str = (today + timedelta(days=2)).strftime("%d/%m")

        return date_str, time_str, people_count

    def handle_reservation(self, user_id, message):
        """Gestiona la reserva asegurándose de solicitar información faltante paso a paso"""
        if user_id not in self.user_reservations:
            self.user_reservations[user_id] = {"date": None, "time": None, "people": None}

        reservation = self.user_reservations[user_id]
        date, time, people = self.extract_details(message)

        if date and not reservation["date"]:
            reservation["date"] = date
            return "📅 Entendido, ¿a qué hora te gustaría reservar?"

        if time and not reservation["time"]:
            reservation["time"] = time

        if reservation["time"] and not reservation["people"]:
            return "👥 Perfecto, ¿para cuántas personas será la reserva?"

        if people and not reservation["people"]:
            reservation["people"] = people

        if all(reservation.values()):
            confirmation = f"✅ Tu reserva está lista para el {reservation['date']} a las {reservation['time']} "\
                           f"para {reservation['people']} personas. ¡Te esperamos en *La Terraza*! 🎉"
            del self.user_reservations[user_id]  # Elimina la reserva tras confirmarla
            return confirmation

        return "Necesito más detalles para completar tu reserva."

reservation_manager = ReservationManager()