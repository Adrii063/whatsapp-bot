import re

class ReservationManager:
    def __init__(self):
        self.user_reservations = {}

    def extract_details(self, message):
        date = re.search(r'(\d{1,2}/\d{1,2}|\d{1,2} de [a-zA-Z]+)', message)
        time = re.search(r'(\d{1,2}:\d{2}|\d{1,2} (?:AM|PM|am|pm))', message)
        people = re.search(r'(\d+)\s*(?:personas?|somos|para)', message)

        return (date.group(0) if date else None, 
                time.group(0) if time else None, 
                people.group(1) if people else None)

    def handle_reservation(self, user_id, message):
        if user_id not in self.user_reservations:
            self.user_reservations[user_id] = {"date": None, "time": None, "people": None}

        details = self.extract_details(message)
        keys = ["date", "time", "people"]
        
        for key, value in zip(keys, details):
            if value and not self.user_reservations[user_id][key]:
                self.user_reservations[user_id][key] = value

        if all(self.user_reservations[user_id].values()):
            confirmation = f"✅ Reserva confirmada para {self.user_reservations[user_id]['date']} "\
                           f"a las {self.user_reservations[user_id]['time']} para "\
                           f"{self.user_reservations[user_id]['people']} personas."
            del self.user_reservations[user_id]  # Limpia después de confirmar
            return confirmation
        return "Necesito más detalles para completar la reserva."

reservation_manager = ReservationManager()

# 🔹 Exportar la función y las reservas activas
handle_reservation = reservation_manager.handle_reservation
user_reservations = reservation_manager.user_reservations