import psycopg2
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# URL de la base de datos
DATABASE_URL = os.getenv("DATABASE_URL")

# Verificar si DATABASE_URL está cargada correctamente
if not DATABASE_URL:
    raise ValueError("❌ ERROR: La variable de entorno DATABASE_URL no está configurada.")

# Conectar a PostgreSQL
try:
    conn = psycopg2.connect(DATABASE_URL)
    cur = conn.cursor()

    # Crear la tabla de reservas
    cur.execute("""
    CREATE TABLE IF NOT EXISTS reservations (
        id SERIAL PRIMARY KEY,
        user_id TEXT UNIQUE NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        people INTEGER NOT NULL
    );
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Base de datos configurada correctamente.")

except Exception as e:
    print(f"❌ Error de conexión: {e}")