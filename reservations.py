import psycopg2
import logging
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

class ReservationManager:
    def __init__(self):
        self.conn = psycopg2.connect(DATABASE_URL)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        """Crea la tabla si no existe."""
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS reservations (
            id SERIAL PRIMARY KEY,
            user_id TEXT NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            people INTEGER NOT NULL
        )
        """)
        self.conn.commit()
        logging.info("✅ Tabla de reservas verificada/creada.")

    def add_reservation(self, user_id, date, time, people):
        """Añade una nueva reserva a la base de datos."""
        try:
            # Convertir fecha al formato DD/MM/YYYY
            formatted_date = self.format_date(date)

            self.cursor.execute("""
                INSERT INTO reservations (user_id, date, time, people)
                VALUES (%s, %s, %s, %s)
            """, (user_id, formatted_date, time, people))

            self.conn.commit()
            logging.info(f"📌 Reserva añadida con éxito para {user_id}: {formatted_date} a las {time}, {people} personas.")
            return True
        except psycopg2.IntegrityError:
            self.conn.rollback()
            logging.error("❌ Ya existe una reserva para este usuario.")
            return False
        except Exception as e:
            self.conn.rollback()
            logging.error(f"❌ Error al añadir la reserva: {e}")
            return False

    def format_date(self, date):
        """Convierte fechas como '2 de febrero' a '02/02/2025'"""
        import datetime

        try:
            if " de " in date:
                day, month = date.split(" de ")
                months = {
                    "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
                    "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
                    "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12"
                }
                return f"{int(day):02}/{months[month]}/2025"
            return date  # Si ya está en formato correcto
        except Exception as e:
            logging.error(f"❌ Error formateando fecha {date}: {e}")
            return date

    def close_connection(self):
        """Cierra la conexión con la base de datos."""
        self.cursor.close()
        self.conn.close()

# Instancia global del manejador de reservas
reservation_manager = ReservationManager()