import secrets
from datetime import datetime

from flask_login import UserMixin

from app.extensions import db, bcrypt


class User(db.Model, UserMixin):
    """
    Benutzerkonto. role="admin" darf im Adminbereich Gigs/Sets/Presskit
    pflegen und Booking-Anfragen bearbeiten. role="user" kann sich nur
    einloggen und Booking-Anfragen stellen.
    api_token wird fuer die Authentifizierung am REST-API verwendet
    (Header: Authorization: Bearer <token>), unabhaengig vom Browser-Login.
    """
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False, default="user")  # "admin" | "user"
    api_token = db.Column(db.String(64), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    bookings = db.relationship("BookingRequest", back_populates="requester", lazy=True)

    def set_password(self, plain_password: str) -> None:
        self.password_hash = bcrypt.generate_password_hash(plain_password).decode("utf-8")

    def check_password(self, plain_password: str) -> bool:
        return bcrypt.check_password_hash(self.password_hash, plain_password)

    def generate_api_token(self) -> str:
        self.api_token = secrets.token_hex(24)
        return self.api_token

    @property
    def is_admin(self) -> bool:
        return self.role == "admin"

    def __repr__(self):
        return f"<User {self.username} ({self.role})>"


class Gig(db.Model):
    """
    Ein Auftritt (bereits gespielt oder in Zukunft geplant).
    status wird beim Anlegen automatisch anhand von event_date gesetzt,
    kann aber ueberschrieben werden (z.B. Gig kurzfristig abgesagt).
    """
    __tablename__ = "gigs"

    id = db.Column(db.Integer, primary_key=True)
    venue = db.Column(db.String(200), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    tag = db.Column(db.String(80), nullable=True)          # z.B. "Opening Set"
    event_date = db.Column(db.Date, nullable=False, index=True)
    status = db.Column(db.String(20), nullable=False, default="upcoming")  # upcoming | past | cancelled
    created_by_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "venue": self.venue,
            "city": self.city,
            "tag": self.tag,
            "event_date": self.event_date.isoformat(),
            "status": self.status,
        }


class SetItem(db.Model):
    """Ein Live-Set / Mix (YouTube oder SoundCloud)."""
    __tablename__ = "sets"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    platform = db.Column(db.String(20), nullable=False)     # "youtube" | "soundcloud"
    video_id = db.Column(db.String(100), nullable=True)
    thumb_url = db.Column(db.String(300), nullable=True)
    external_url = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "platform": self.platform,
            "video_id": self.video_id,
            "thumb_url": self.thumb_url,
            "external_url": self.external_url,
        }


class PressItem(db.Model):
    """Presskit-Datei oder -Link (PDF, ZIP, externer Ordner)."""
    __tablename__ = "press_items"

    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)   # "pdf" | "zip" | "link"
    title = db.Column(db.String(150), nullable=False)
    file_url = db.Column(db.String(300), nullable=False)

    def to_dict(self):
        return {"id": self.id, "type": self.type, "title": self.title, "file_url": self.file_url}


class BookingRequest(db.Model):
    """
    Buchungsanfrage eines Veranstalters/Bookers.
    Das ist die zentrale Geschaeftslogik der Applikation:
    - Ein eingeloggter User stellt eine Anfrage fuer ein Datum/Ort.
    - Der Admin sieht alle Anfragen und kann sie annehmen oder ablehnen.
    - Beim Annehmen wird geprueft, ob am selben Datum bereits ein
      bestaetigter Gig existiert (Konfliktpruefung) - siehe
      app/booking/routes.py::accept_booking().
    - Wird eine Anfrage angenommen, wird automatisch ein Gig-Eintrag erzeugt.
    """
    __tablename__ = "booking_requests"

    id = db.Column(db.Integer, primary_key=True)
    requester_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    requester_name = db.Column(db.String(150), nullable=False)
    requester_email = db.Column(db.String(120), nullable=False)
    event_date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(200), nullable=True)
    message = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(20), nullable=False, default="pending")  # pending | accepted | declined
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    requester = db.relationship("User", back_populates="bookings")

    def to_dict(self):
        return {
            "id": self.id,
            "requester_name": self.requester_name,
            "requester_email": self.requester_email,
            "event_date": self.event_date.isoformat(),
            "location": self.location,
            "message": self.message,
            "status": self.status,
        }
