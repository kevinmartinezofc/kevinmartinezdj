"""
Einmaliges Update fuer die bereits laufende Datenbank:
1. Fuegt die neue Spalte 'gated' zur Tabelle press_items hinzu
   (noetig, weil db.create_all() bestehende Tabellen nicht veraendert).
2. Markiert den vorhandenen "Full EPK"-Eintrag als gated=True, damit
   Demo-Tracks/Sets nur fuer eingeloggte User sichtbar sind.

Aufruf (mit externer Render-DATABASE_URL, wie bei den vorherigen Scripts):
  $env:DATABASE_URL = "postgresql://<externe-url>"
  python add_marketing_features.py
"""
from sqlalchemy import text

from app import create_app
from app.extensions import db
from app.models import PressItem

app = create_app()

with app.app_context():
    # 1. Spalte hinzufuegen (idempotent - laeuft auch mehrfach ohne Fehler)
    try:
        db.session.execute(text(
            "ALTER TABLE press_items ADD COLUMN gated BOOLEAN NOT NULL DEFAULT FALSE"
        ))
        db.session.commit()
        print("Spalte 'gated' hinzugefuegt.")
    except Exception as e:
        db.session.rollback()
        print(f"Spalte existiert vermutlich schon (ok): {e}")

    # 2. Full EPK als gesperrt markieren
    epk = PressItem.query.filter_by(title="Full EPK").first()
    if epk:
        epk.gated = True
        db.session.commit()
        print("'Full EPK' ist jetzt hinter Login gesperrt.")
    else:
        print("Kein 'Full EPK'-Eintrag gefunden - nichts zu markieren.")

    print("Fertig.")
