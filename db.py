import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import logging

# Cargar variables de entorno
load_dotenv()

# Configurar logs
logging.basicConfig(level=logging.INFO)

class Database:
    def __init__(self):
        try:
            self.conn = psycopg2.connect(
                dbname=os.getenv("DB_NAME"),
                user=os.getenv("DB_USER"),
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT")
            )
            self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
            self.create_table()
            logging.info("✅ Conexión exitosa a la base de datos")
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

    def add_reservation(self, user_id, date, time, people):
        """Agrega una nueva reserva en la base de datos."""
        try:
            logging.info(f"📝 Intentando agregar reserva para {user_id}: {date} {time}, {people} personas")
            self.cur.execute("""
                INSERT INTO reservations (user_id, date, time, people) 
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE 
                SET date = EXCLUDED.date, time = EXCLUDED.time, people = EXCLUDED.people;
            """, (user_id, date, time, people))
            self.conn.commit()
            logging.info("✅ Reserva guardada exitosamente")
        except Exception as e:
            logging.error(f"❌ Error al guardar reserva: {e}")

    def get_reservation(self, user_id):
        """Obtiene una reserva de un usuario."""
        try:
            self.cur.execute("SELECT * FROM reservations WHERE user_id = %s", (user_id,))
            reserva = self.cur.fetchone()
            logging.info(f"🔍 Reserva encontrada para {user_id}: {reserva}")
            return reserva
        except Exception as e:
            logging.error(f"❌ Error al obtener reserva: {e}")
            return None

    def delete_reservation(self, user_id):
        """Elimina la reserva de un usuario."""
        try:
            self.cur.execute("DELETE FROM reservations WHERE user_id = %s", (user_id,))
            self.conn.commit()
            logging.info(f"🗑️ Reserva eliminada para {user_id}")
        except Exception as e:
            logging.error(f"❌ Error al eliminar reserva: {e}")

    def close_connection(self):
        """Cierra la conexión con la base de datos."""
        self.cur.close()
        self.conn.close()
        logging.info("🔌 Conexión cerrada con la base de datos")

# Instancia global de la base de datos
db = Database()