import os
from dotenv import load_dotenv

# Cargar variables de entorno desde .env
load_dotenv()

# Configuración global
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASE_URL = "https://openrouter.ai/api/v1"
PORT = int(os.getenv("PORT", 5000))

# Configuración de PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL")