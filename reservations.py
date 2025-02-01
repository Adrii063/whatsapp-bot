import psycopg2
import logging
import os
from dotenv import load_dotenv
import re
from datetime import datetime

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
            user_id TEXT UNIQUE NOT NULL,
            date TEXT NOT NULL,
            time TEXT NOT NULL,
            people INTEGER NOT NULL
        )
        """)
        self.conn.commit()
        logging.info("✅ Tabla de reservas verificada/creada.")

    def normalize_date(self, date_text):
        """Convierte una fecha en formato 'D de mes' o 'D/M' al formato DD/MM/AAAA."""
        try:
            meses = {
                "enero": "01", "febrero": "02", "marzo": "03", "abril": "04",
                "mayo": "05", "junio": "06", "julio": "07", "agosto": "08",
                "septiembre": "09", "octubre": "10", "noviembre": "11", "diciembre": "12"
            }
            
            # Verificar si está en formato "D de mes"
            match = re.match(r"(\d{1,2}) de (\w+)", date_text)
            if match:
                day, month_text = match.groups()
                month = meses.get(month_text.lower())
                year = datetime.now().year  # Año actual
                return f"{int(day):02d}/{month}/{year}"

            # Verificar si está en formato "D/M"
            match = re.match(r"(\d{1,2})/(\d{1,2})", date_text)
            if match:
                day, month = match.groups()
                year = datetime.now().year  # Año actual
                return f"{int(day):02d}/{int(month):02d}/{year}"

            return date_text  # Si ya está bien, lo dejamos igual

        except Exception as e:
            logging.error(f"❌ Error al normalizar la fecha: {e}")
            return date_text  # Devolver sin cambios en caso de error

    def add_reservation(self, user_id, date, time, people):
        """Añade una nueva reserva a la base de datos."""
        try:
            date = self.normalize_date(date)  # Normalizar fecha antes de insertar

            self.cursor.execute("""
                INSERT INTO reservations (user_id, date, time, people) VALUES (%s, %s, %s, %s)
            """, (user_id, date, time, people))
            self.conn.commit()
            logging.info(f"📌 Reserva añadida con éxito para {user_id}: {date} a las {time}, {people} personas.")
        except psycopg2.IntegrityError:
            self.conn.rollback()
            logging.error("❌ Ya existe una reserva para este usuario.")
            raise Exception("Este usuario ya tiene una reserva.")
        except Exception as e:
            self.conn.rollback()
            logging.error(f"❌ Error al añadir la reserva: {e}")
            raise e

    def close_connection(self):
        """Cierra la conexión con la base de datos."""
        self.cursor.close()
        self.conn.close()

# Instancia global del manejador de reservas
reservation_manager = ReservationManager()