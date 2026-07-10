"""
Fuellt die Datenbank mit Demo-Daten (Gigs, Sets, Presskit), damit die
Startseite nach der Ersteinrichtung nicht leer ist.
Aufruf:  python seed.py
"""
from datetime import date

from app import create_app
from app.extensions import db
from app.models import Gig, SetItem, PressItem

app = create_app()

with app.app_context():
    if Gig.query.count() == 0:
        db.session.add_all([
            Gig(venue="Bügelbrett x Tamarindo Art @ Kraftwerk", city="Zürich, CH",
                tag="Maintime", event_date=date(2026, 7, 25), status="upcoming"),
            Gig(venue="Terrazzza @ Horse Park Festival", city="Dielsdorf, CH",
                tag="Welcome Stage", event_date=date(2026, 6, 15), status="past"),
            Gig(venue="Cafe Bar Black 1966", city="Zürich, CH",
                tag="Maintime", event_date=date(2026, 6, 5), status="past"),
        ])

    if SetItem.query.count() == 0:
        db.session.add_all([
            SetItem(title="Summer Grooves | Live @ Terrazzza Welcome Stage",
                    platform="soundcloud", thumb_url="/static/images/terrazzza.jpeg",
                    external_url="https://on.soundcloud.com/mjnp7S6EMxBai7bVNB"),
            SetItem(title="DJ Retreat 2026 | Terrace DJ Live Set",
                    platform="youtube", video_id="BpFuLNJQmUQ",
                    external_url="https://youtu.be/BpFuLNJQmUQ"),
        ])

    if PressItem.query.count() == 0:
        db.session.add_all([
            PressItem(type="pdf", title="Biografie", file_url="/static/files/KEVN_MARTINEZ_Presskit.pdf"),
            PressItem(type="zip", title="Pressefotos", file_url="/static/files/PHOTOS.zip"),
            PressItem(type="link", title="Full EPK",
                      file_url="https://drive.google.com/drive/folders/1b5oLOned5Zqsk5WAZ9N0EfkkB3RFWRX1"),
        ])

    db.session.commit()
    print("Demo-Daten eingefuegt.")
