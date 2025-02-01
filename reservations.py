from db import db
import re
import logging

# Configurar logging para debug
test_logger = logging.getLogger("reservations_logger")
test_logger.setLevel(logging.INFO)

class ReservationManager:
    def __init__(self):
        self.pending_reservations = {}
    
    def extract_details(self, message):
        """Extrae fecha, hora y número de personas de un mensaje."""
        date_match = re.search(r'(\d{1,2}/\d{1,2}|\d{1,2} de [a-zA-Z]+)', message)
        time_match = re.search(r'(\d{1,2}[:h]\d{2}|\d{1,2} (?:AM|PM|am|pm))', message)
        people_match = re.search(r'(\d+)\s*(?:personas?|somos|para)', message)
        
        date = date_match.group(0) if date_match else None
        time = time_match.group(0) if time_match else None
        people = int(people_match.group(1)) if people_match else None
        
        return date, time, people
    
    def handle_reservation(self, user_id, message):
        """Gestiona el proceso de reserva."""
        
        test_logger.info(f"📩 Mensaje recibido de {user_id}: {message}")
        
        # Extraer datos
        date, time, people = self.extract_details(message)
        
        # Si el usuario no ha proporcionado toda la info, preguntar
        if not date or not time or not people:
            self.pending_reservations[user_id] = {"date": date, "time": time, "people": people}
            missing_info = []
            if not date:
                missing_info.append("fecha")
            if not time:
                missing_info.append("hora")
            if not people:
                missing_info.append("número de personas")
            return f"Necesito más detalles para la reserva. ¿Podrías indicarme {', '.join(missing_info)}?"
        
        # Guardar reserva en la base de datos
        test_logger.info(f"📝 Insertando en DB: {user_id}, {date}, {time}, {people}")
        db.add_reservation(user_id, date, time, people)
        test_logger.info("✅ Reserva guardada exitosamente")
        
        return f"¡Reserva confirmada para {people} personas el {date} a las {time}! ¿Puedo ayudarte en algo más? 😊"
    
    def get_user_reservation(self, user_id):
        """Obtiene la reserva de un usuario."""
        reservation = db.get_reservation(user_id)
        if reservation:
            return f"🔍 Tienes una reserva para {reservation['people']} personas el {reservation['date']} a las {reservation['time']}."
        else:
            return "No tienes reservas activas en este momento."
    
    def cancel_reservation(self, user_id):
        """Cancela la reserva de un usuario."""
        reservation = db.get_reservation(user_id)
        if reservation:
            db.delete_reservation(user_id)
            return "❌ Tu reserva ha sido cancelada con éxito."
        else:
            return "⚠️ No tienes ninguna reserva activa para cancelar."

# Crear instancia global
reservation_manager = ReservationManager()