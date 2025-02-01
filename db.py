import os
import psycopg2
import logging
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Configurar logs
logging.basicConfig(level=logging.DEBUG)

# Cargar variables de entorno
load_dotenv()

class Database:
    def __init__(self):
        try:
            logging.info("🔹 Conectando a la base de datos...")
            self.conn = psycopg2.connect(os.getenv("DATABASE_URL"), cursor_factory=RealDictCursor)
            self.cur = self.conn.cursor()
            self.create_table()
            logging.info("✅ Conexión a la base de datos establecida correctamente.")
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
        logging.info("✅ Tabla de reservas verificada/creada.")

    def add_reservation(self, user_id, date, time, people):
        """Agrega una nueva reserva en la base de datos."""
        try:
            logging.debug(f"📝 Intentando agregar reserva para {user_id}: {date} {time}, {people} personas")
            self.cur.execute("""
                INSERT INTO reservations (user_id, date, time, people) 
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (user_id) DO UPDATE 
                SET date = EXCLUDED.date, time = EXCLUDED.time, people = EXCLUDED.people;
            """, (user_id, date, time, people))
            self.conn.commit()
            logging.info("✅ Reserva guardada exitosamente")
        except Exception as e:
            logging.error(f"❌ Error al agregar la reserva: {e}")

    def get_reservation(self, user_id):
        """Obtiene una reserva de un usuario."""
        self.cur.execute("SELECT * FROM reservations WHERE user_id = %s", (user_id,))
        return self.cur.fetchone()

    def delete_reservation(self, user_id):
        """Elimina la reserva de un usuario."""
        self.cur.execute("DELETE FROM reservations WHERE user_id = %s", (user_id,))
        self.conn.commit()

    def close_connection(self):
        """Cierra la conexión con la base de datos."""
        self.cur.close()
        self.conn.close()

# Instancia global de la base de datos
db = Database()