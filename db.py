import os
import psycopg2
import logging
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Database:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT"),
                sslmode="require"
            )
            self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
            logging.info("✅ Conexión exitosa a la base de datos")
            self.create_table()
        except Exception as e:
            logging.error(f"❌ Error al conectar a la base de datos: {e}")

    def create_table(self):
        """Crea la tabla de reservas si no existe."""
        self.cur.execute("""
            CREATE TABLE IF NOT EXISTS reservations (
                id SERIAL PRIMARY KEY,
                user_id TEXT UNIQUE NOT NULL,
                date TEXT NOT NULL,
                time TEXT NOT NULL,
                people INTEGER NOT NULL
            );
        """)
        self.conn.commit()
        logging.info("📌 Tabla de reservas asegurada.")

    def add_reservation(self, user_id, date, time, people):
        """Agrega una nueva reserva en la base de datos."""
        logging.info(f"📝 Intentando agregar reserva para {user_id}: {date} {time}, {people} personas")
        try:
            self.cur.execute("""
                INSERT INTO reservations (user_id, date, time, people) 
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE 
                SET date = EXCLUDED.date, time = EXCLUDED.time, people = EXCLUDED.people;
            """, (user_id, date, time, people))
            self.conn.commit()
            logging.info("✅ Reserva guardada exitosamente")
        except Exception as e:
            logging.error(f"❌ Error al guardar la reserva: {e}")

    def get_reservation(self, user_id):
        """Obtiene una reserva de un usuario."""
        self.cur.execute("SELECT * FROM reservations WHERE user_id = %s", (user_id,))
        reserva = self.cur.fetchone()
        logging.info(f"🔍 Reserva encontrada para {user_id}: {reserva}")
        return reserva

    def delete_reservation(self, user_id):
        """Elimina la reserva de un usuario."""
        self.cur.execute("DELETE FROM reservations WHERE user_id = %s", (user_id,))
        self.conn.commit()
        logging.info(f"❌ Reserva eliminada para {user_id}")

    def close_connection(self):
        """Cierra la conexión con la base de datos."""
        self.cur.close()
        self.conn.close()
        logging.info("🔴 Conexión a la base de datos cerrada.")

# Instancia global de la base de datos
db = Database()