import logging
from db import db

class ReservationManager:
    def __init__(self):
        logging.info("🔹 Manejador de reservas inicializado")

    def handle_reservation(self, user_id, date, time, people):
        """Guarda la reserva en la base de datos"""
        try:
            logging.info(f"📝 Intentando agregar reserva para {user_id}: {date} {time}, {people} personas")
            db.add_reservation(user_id, date, time, people)
            logging.info(f"✅ Reserva guardada correctamente para {user_id}")
            return f"Reserva confirmada: {date} a las {time} para {people} personas."
        except Exception as e:
            logging.error(f"❌ ERROR al guardar reserva en DB: {e}")
            return "Hubo un problema con tu reserva, intenta más tarde."

reservation_manager = ReservationManager()