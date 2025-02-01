import os
import psycopg2
import logging
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Obtener la URL de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    logging.error("❌ ERROR: La variable de entorno DATABASE_URL no está configurada.")
    raise ValueError("DATABASE_URL no está definida en el entorno.")

class Database:
    def __init__(self):
        logging.info("🔹 Conectando a la base de datos...")
        try:
            self.conn = psycopg2.connect(DATABASE_URL, sslmode='require')
            self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
            self.create_table()
            logging.info("✅ Conexión a la base de datos establecida correctamente.")
        except Exception as e:
            logging.error(f"❌ Error al conectar a la base de datos: {e}")
            self.conn = None
            self.cur = None

    def create_table(self):
        """Crea la tabla de reservas si no existe."""
        if self.conn and self.cur:
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
            logging.info("✅ Tabla de reservas verificada/creada.")

    def add_reservation(self, user_id, date, time, people):
        """Agrega una nueva reserva en la base de datos."""
        if not self.conn or not self.cur:
            logging.error("❌ No hay conexión a la base de datos. No se puede agregar la reserva.")
            return
        
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
        if not self.conn or not self.cur:
            logging.error("❌ No hay conexión a la base de datos. No se pueden obtener reservas.")
            return None
        
        logging.info(f"🔍 Buscando reserva para {user_id}")
        self.cur.execute("SELECT * FROM reservations WHERE user_id = %s", (user_id,))
        reservation = self.cur.fetchone()
        if reservation:
            logging.info(f"📌 Reserva encontrada: {reservation}")
        return reservation

    def delete_reservation(self, user_id):
        """Elimina la reserva de un usuario."""
        if not self.conn or not self.cur:
            logging.error("❌ No hay conexión a la base de datos. No se pueden eliminar reservas.")
            return
        
        logging.info(f"❌ Eliminando reserva para {user_id}")
        self.cur.execute("DELETE FROM reservations WHERE user_id = %s", (user_id,))
        self.conn.commit()
        logging.info("✅ Reserva eliminada correctamente.")

    def close_connection(self):
        """Cierra la conexión con la base de datos."""
        if self.cur:
            self.cur.close()
        if self.conn:
            self.conn.close()
        logging.info("🔌 Conexión a la base de datos cerrada.")

# Instancia global de la base de datos
db = Database()