"""
Migriert die echten Inhalte aus der alten statischen HTML-Seite
(UPCOMING_LIST, GIGS_LIST, SETS_LIST, Presskit) in die neue Datenbank.

WICHTIG: Bei den vergangenen Gigs stand im alten Code nur "Monat + Jahr"
(z.B. "JUN 2026"), kein genauer Tag. Hier wird deshalb der 1. des Monats
als Platzhalter-Datum verwendet. Falls dir die genauen Tage noch bekannt
sind, kannst du sie danach bequem im Admin-Dashboard (/admin) korrigieren.

Aufruf:
  1. .env (lokal) tempor√§r auf die Render-DATABASE_URL setzen
     (External Database URL von Render kopieren, NICHT Internal)
  2. python migrate_legacy_data.py
  3. .env danach wieder zurücksetzen (oder .env.production separat halten)
"""
from datetime import date

from app import create_app
from app.extensions import db
from app.models import Gig, SetItem, PressItem

app = create_app()

MONTH_MAP = {
    "JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
    "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12,
}

UPCOMING_LIST = [
    {"date": "JUL 25 2026", "venue": "Bügelbrett x Tamarindo Art @ Kraftwerk",
     "city": "Zürich, CH", "tag": "Maintime"},
]

GIGS_LIST = [
    {"date": "JUN 2026", "venue": "Terrazzza @ Horse Park Festival", "city": "Dielsdorf, CH", "tag": "Welcome Stage"},
    {"date": "JUN 2026", "venue": "Cafe Bar Black 1966", "city": "Zürich, CH", "tag": "Maintime"},
    {"date": "JUN 2026", "venue": "Samaia @ Roof61", "city": "Zürich, CH", "tag": "B2B Closing Set"},
    {"date": "MAY 2026", "venue": "Valeo Rooftop Party", "city": "Zürich, CH", "tag": "Opening Set"},
    {"date": "MAY 2026", "venue": "Echo @ Club Bellevue", "city": "Zürich, CH", "tag": "B2B Closing Set"},
    {"date": "MAY 2026", "venue": "Bügelbrett @ Kraftwerk", "city": "Zürich, CH", "tag": "Opening Set"},
    {"date": "APR 2026", "venue": "Ostertanz @ Club Bellevue", "city": "Zürich, CH", "tag": "Opening Set"},
    {"date": "FEB 2026", "venue": "Kurz Vor Tanz @ Supermarket", "city": "Zürich, CH", "tag": "Closing Set"},
    {"date": "DEC 2025", "venue": "Kurz Vor Tanz @ Club Bellevue", "city": "Zürich, CH", "tag": "Opening Set"},
]

SETS_LIST = [
    {"title": "Summer Grooves | Live @ Terrazzza Welcome Stage | KEV:N MARTINEZ",
     "platform": "soundcloud", "thumb_url": "/static/images/terrazzza.jpeg",
     "external_url": "https://on.soundcloud.com/mjnp7S6EMxBai7bVNB"},
    {"title": "DJ Retreat 2026 | Terrace DJ Live Set",
     "platform": "youtube", "video_id": "BpFuLNJQmUQ",
     "external_url": "https://youtu.be/BpFuLNJQmUQ?t=3649"},
    {"title": "late mornings & house grooves",
     "platform": "soundcloud", "thumb_url": "/static/images/latemorning.JPG",
     "external_url": "https://on.soundcloud.com/D4BqxBj0J8IHhCdpm6"},
    {"title": "TRIBAL AWAKENING - Afro Tech | KEV:N MARTINEZ",
     "platform": "soundcloud", "thumb_url": "/static/images/IMG_7550.jpg",
     "external_url": "https://on.soundcloud.com/JVKKud24HI7fFXNfjU"},
    {"title": "FUNDA LA SOL B2B KEV:N MARTINEZ - Tech-House Set | Colmar, France",
     "platform": "youtube", "video_id": "Ih4RW7lGpYY",
     "external_url": "https://youtu.be/Ih4RW7lGpYY"},
    {"title": "KEV:N MARTINEZ - Pulse (Extended Version) [FREE DL]",
     "platform": "soundcloud", "thumb_url": "/static/images/Pulse.png",
     "external_url": "https://on.soundcloud.com/sdBPeGJLmOjRyPaADb"},
]

PRESS_ITEMS = [
    {"type": "pdf", "title": "Biografie", "file_url": "/static/files/KEVN_MARTINEZ_Presskit.pdf"},
    {"type": "link", "title": "Full EPK",
     "file_url": "https://drive.google.com/drive/folders/1b5oLOned5Zqsk5WAZ9N0EfkkB3RFWRX1?usp=sharing"},
]


def parse_date(s: str) -> date:
    parts = s.split()
    if len(parts) == 3:          # "JUL 25 2026"
        month, day, year = parts
        return date(int(year), MONTH_MAP[month], int(day))
    else:                        # "JUN 2026" -> 1. des Monats als Platzhalter
        month, year = parts
        return date(int(year), MONTH_MAP[month], 1)


with app.app_context():
    added_gigs = 0
    for item in UPCOMING_LIST:
        d = parse_date(item["date"])
        if not Gig.query.filter_by(venue=item["venue"], event_date=d).first():
            db.session.add(Gig(venue=item["venue"], city=item["city"], tag=item["tag"],
                                event_date=d, status="upcoming"))
            added_gigs += 1

    for item in GIGS_LIST:
        d = parse_date(item["date"])
        if not Gig.query.filter_by(venue=item["venue"], event_date=d).first():
            db.session.add(Gig(venue=item["venue"], city=item["city"], tag=item["tag"],
                                event_date=d, status="past"))
            added_gigs += 1

    added_sets = 0
    for item in SETS_LIST:
        if not SetItem.query.filter_by(title=item["title"]).first():
            db.session.add(SetItem(
                title=item["title"], platform=item["platform"],
                video_id=item.get("video_id"), thumb_url=item.get("thumb_url"),
                external_url=item["external_url"],
            ))
            added_sets += 1

    added_press = 0
    for item in PRESS_ITEMS:
        if not PressItem.query.filter_by(title=item["title"]).first():
            db.session.add(PressItem(**item))
            added_press += 1

    db.session.commit()
    print(f"Migration abgeschlossen: {added_gigs} Gigs, {added_sets} Sets, {added_press} Presskit-Eintraege hinzugefuegt.")
    print("Hinweis: Vergangene Gigs haben als Platzhalter den 1. des jeweiligen Monats.")
    print("Genaue Tage kannst du im Admin-Dashboard (/admin) nachtragen.")
