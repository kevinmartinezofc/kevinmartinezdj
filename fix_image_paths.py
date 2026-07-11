"""
Einmaliges Korrektur-Script: behebt Gross-/Kleinschreibungs-Fehler bei den
thumb_url-Pfaden der SetItem-Eintraege, die durch migrate_legacy_data.py
mit falscher Schreibweise angelegt wurden (Windows ist da tolerant,
Render/Linux nicht).

Aufruf (mit externer Render-DATABASE_URL, wie bei der Migration):
  $env:DATABASE_URL = "postgresql://<externe-url>"
  python fix_image_paths.py
"""
from app import create_app
from app.extensions import db
from app.models import SetItem

app = create_app()

# Falscher Pfad -> korrekter Pfad (exakt wie die Datei tatsaechlich heisst)
CORRECTIONS = {
    "/static/images/latemorning.JPG": "/static/images/latemorning.jpg",
    "/static/images/IMG_7550.jpg": "/static/images/img_7550.jpg",
    "/static/images/Pulse.png": "/static/images/pulse.png",
}

with app.app_context():
    fixed = 0
    for wrong, correct in CORRECTIONS.items():
        item = SetItem.query.filter_by(thumb_url=wrong).first()
        if item:
            item.thumb_url = correct
            fixed += 1
            print(f"Korrigiert: '{item.title}' -> {correct}")

    db.session.commit()
    print(f"\nFertig. {fixed} Eintraege korrigiert.")
