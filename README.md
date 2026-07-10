# KEV:N MARTINEZ — DJ Booking Web App

Praxisarbeit DBWE.TA1A.PA — Flask-Webanwendung mit relationaler Datenbank,
Benutzerkonten, eigener Geschäftslogik (Booking-Workflow) und REST-API.

## 1. Funktionsumfang

- **Öffentliche Seite**: Portfolio (About, Live Sets, Gigs, Presskit) — Daten
  kommen aus der Datenbank statt aus fest codierten JS-Arrays.
- **Benutzerkonten**: Registrierung (Username + E-Mail + Passwort, gehasht
  mit bcrypt), Login/Logout. Der erste registrierte User wird automatisch
  Admin.
- **Booking-Workflow (Geschäftslogik)**: Eingeloggte User können eine
  Buchungsanfrage stellen. Admins sehen alle Anfragen im Dashboard und
  können sie annehmen/ablehnen. Beim Annehmen wird geprüft, ob am selben
  Datum bereits ein Gig existiert (Konfliktprüfung) — falls ja, wird die
  Annahme verweigert. Wird die Anfrage angenommen, wird automatisch ein
  Gig-Eintrag erzeugt.
- **Admin-Dashboard**: Gigs und Live-Sets können direkt über die Weboberfläche
  gepflegt werden (kein manuelles Code-Editieren mehr nötig).
- **REST-API**:
  - `GET /api/gigs` — öffentlich, liefert alle Gigs als JSON
  - `GET /api/gigs/<id>` — öffentlich
  - `GET /api/sets` — öffentlich
  - `GET /api/bookings` — **geschützt**, benötigt
    `Authorization: Bearer <token>` (Token ist im Admin-Dashboard sichtbar)

## 2. Technologie-Stack

| Komponente      | Technologie                                   |
|------------------|------------------------------------------------|
| Sprache          | Python ≥ 3.9                                   |
| Web-Framework    | Flask 3 (+ Flask-SQLAlchemy, Flask-Login, Flask-Bcrypt) |
| Datenbank        | SQLite (lokale Entwicklung) / PostgreSQL oder MySQL (Produktion) |
| Webserver        | Gunicorn (optional hinter Nginx)               |
| Frontend         | Jinja2-Templates, bestehendes CSS-Design       |

## 3. Lokale Installation

```bash
python3 -m venv venv
source venv/bin/activate            # Windows: venv\Scripts\activate
pip install -r requirements.txt

cp .env.example .env                # SECRET_KEY anpassen

python run.py                       # Startet auf http://localhost:5000
python seed.py                      # (optional) Demo-Daten einfügen
```

Danach `http://localhost:5000/register` öffnen und einen Account anlegen —
der erste registrierte Account ist automatisch Admin und erhält ein
API-Token (sichtbar unter `/admin`).

## 4. Produktions-Deployment (Beispiel Ubuntu-Server)

```bash
# 1. PostgreSQL-Datenbank anlegen
sudo -u postgres createdb dj_booking
sudo -u postgres createuser dj_user --pwprompt

# 2. .env auf dem Server anpassen
DATABASE_URL=postgresql://dj_user:PASSWORT@localhost:5432/dj_booking
SECRET_KEY=<langer-zufalls-string>

# 3. Abhängigkeiten installieren
pip install -r requirements.txt

# 4. Mit Gunicorn starten
gunicorn -w 4 -b 0.0.0.0:8000 run:app

# 5. (empfohlen) Nginx als Reverse-Proxy davorschalten für HTTPS
```

Zugriff nach Deployment (Beispiel — mit tatsächlicher Server-IP/Domain zu
ersetzen und im Lösungsdokument zu dokumentieren):
- Web: `https://<host>:8000/`
- API: `https://<host>:8000/api/gigs`
- Login-Testkonto: siehe Abgabedokumentation

## 5. Tests

```bash
pip install pytest
pytest -v
```

Die Tests decken ab: Registrierung, Login, Rollenmodell (erster User = Admin),
Booking-Workflow inkl. Datumsvalidierung, Konfliktprüfung bei der Gig-Annahme,
Zugriffsschutz des Admin-Bereichs und Authentifizierung des API.

Ein manuelles Testprotokoll mit 6–12 Testfällen liegt in `TESTPROTOKOLL.md`.

## 6. Projektstruktur

```
dj-booking-app/
├── app/
│   ├── __init__.py          # App-Factory
│   ├── extensions.py        # db, login_manager, bcrypt
│   ├── models.py            # User, Gig, SetItem, PressItem, BookingRequest
│   ├── auth/routes.py       # Registrierung, Login, Logout
│   ├── main/routes.py       # Öffentliche Startseite
│   ├── booking/routes.py    # Booking-Workflow + Admin-CRUD
│   ├── api/routes.py        # REST-API inkl. Token-Auth
│   ├── templates/           # Jinja2-Templates
│   └── static/              # CSS, Bilder
├── tests/test_app.py
├── seed.py
├── config.py
├── run.py
└── requirements.txt
```

## 7. Quellenangaben

Der Basis-Code für Flask-App-Factory, Flask-Login-Integration und
Flask-SQLAlchemy-Modelle folgt den Standardmustern aus der offiziellen
Flask-Dokumentation (flask.palletsprojects.com) und den Erweiterungs-Docs
von Flask-Login / Flask-SQLAlchemy / Flask-Bcrypt.
