"""
Zentrale Instanzen der Flask-Erweiterungen.
Getrennt von __init__.py ausgelagert, damit andere Module (models.py,
routes.py) sie importieren koennen, ohne einen zirkulaeren Import mit der
App-Factory zu erzeugen.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
login_manager.login_message = "Bitte melde dich an, um fortzufahren."
login_manager.login_message_category = "info"
