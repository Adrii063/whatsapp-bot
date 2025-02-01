import logging
from db import db

class ReservationManager:
    def __init__(self):
        logging.debug("🔹 Manejador de reservas inicializado")

    def handle_reservation(self, user_id, date, time, people):
        """Guarda la reserva en la base de datos"""
        try:
            logging.info(f"📝 Intentando agregar reserva para {user_id}: {date} {time}, {people} personas")
            db.add_reservation(user_id, date, time, people)
            logging.info(f"✅ Reserva guardada correctamente en la base de datos para {user_id}")
            return f"Tu reserva para el {date} a las {time} para {people} personas ha sido confirmada. ¡Te esperamos en *La Terraza*! 🎉"
        except Exception as e:
            logging.error(f"❌ Error al guardar la reserva en la base de datos: {e}")
            return "Hubo un error al procesar tu reserva. Por favor, intenta de nuevo más tarde."

reservation_manager = ReservationManager()