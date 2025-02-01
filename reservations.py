import psycopg2
import logging
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

class ReservationManager:
    def __init__(self):
        """Inicializa la conexión con la base de datos y verifica la tabla."""
        self.conn = psycopg2.connect(DATABASE_URL)
        self.conn.autocommit = True  # Evita problemas de commit pendientes
        self.create_table()

    def create_table(self):
        """Crea la tabla de reservas si no existe."""
        with self.conn.cursor() as cursor:
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS reservations (
                id SERIAL PRIMARY KEY,
                user_id TEXT UNIQUE NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                people INTEGER NOT NULL
            )
            """)
        logging.info("✅ Tabla de reservas verificada/creada.")

    def add_reservation(self, user_id, date, time, people):
        """Añade una nueva reserva a la base de datos."""
        try:
            with self.conn.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO reservations (user_id, date, time, people)
                    VALUES (%s, %s, %s, %s)
                """, (user_id, date, time, people))
            logging.info(f"📌 Reserva añadida con éxito para {user_id}: {date} a las {time}, {people} personas.")
            return True
        except psycopg2.IntegrityError:
            logging.error("❌ Ya existe una reserva para este usuario.")
            raise Exception("Este usuario ya tiene una reserva.")
        except Exception as e:
            logging.error(f"❌ Error al añadir la reserva: {e}")
            raise e

    def close_connection(self):
        """Cierra la conexión con la base de datos."""
        if self.conn:
            self.conn.close()
            logging.info("🔻 Conexión con la base de datos cerrada.")

# Instancia global del manejador de reservas
reservation_manager = ReservationManager()