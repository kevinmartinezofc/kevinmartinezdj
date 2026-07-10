import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    """
    Zentrale Konfiguration der Applikation.
    Alle sensiblen Werte (Secret Key, DB-Zugang) werden aus Umgebungsvariablen
    gelesen -> siehe .env.example. So landen keine Passwoerter im Source Code.
    """
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")

    # Standardmaessig SQLite fuer lokale Entwicklung. Fuer Produktion wird
    # DATABASE_URL gesetzt, z.B.:
    #   postgresql://user:password@host:5432/dbname
    #   mysql+pymysql://user:password@host:3306/dbname
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", f"sqlite:///{os.path.join(BASE_DIR, 'dev.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Wird beim Registrieren des allerersten Users automatisch zum Admin
    # gemacht (siehe app/auth/routes.py) - so ist ohne CLI immer ein
    # Admin-Konto vorhanden.
