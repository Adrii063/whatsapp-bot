import os
import psycopg2
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
                host=os.getenv("DB_HOST"),  # ✅ Usa la URL completa de la base de datos
                port=os.getenv("DB_PORT")
            )
            self.cur = self.conn.cursor(cursor_factory=RealDictCursor)
            self.create_table()
            print("✅ Conexión a la base de datos exitosa.")
        except Exception as e:
            print(f"❌ Error al conectar a la base de datos: {e}")

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
        self.cur.execute("""
            INSERT INTO reservations (user_id, date, time, people) 
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (user_id) DO UPDATE 
            SET date = EXCLUDED.date, time = EXCLUDED.time, people = EXCLUDED.people;
        """, (user_id, date, time, people))
        self.conn.commit()

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