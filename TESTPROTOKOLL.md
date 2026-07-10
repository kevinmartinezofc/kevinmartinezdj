# Testprotokoll — KEV:N MARTINEZ DJ Booking App

Automatisiert nachvollziehbar über `pytest tests/test_app.py -v`.
Alle Tests unten entsprechen jeweils einer Funktion in `test_app.py`.

| # | Testfall | Erwartetes Ergebnis | Tatsächliches Ergebnis |
|---|----------|----------------------|--------------------------|
| 1 | Startseite aufrufen (`GET /`) | HTTP 200, Seite enthält Künstlername | ✅ Bestanden |
| 2 | Registrierung mit gültigen Daten | User wird in DB angelegt | ✅ Bestanden |
| 3 | Erster registrierter User | Erhält automatisch Rolle "admin" + API-Token | ✅ Bestanden |
| 4 | Registrierung mit bereits vergebenem Benutzernamen | Fehlermeldung, kein zweiter User angelegt | ✅ Bestanden |
| 5 | Login mit falschem Passwort | Fehlermeldung, kein Login | ✅ Bestanden |
| 6 | Login mit korrekten Daten | Erfolgreicher Login, Begrüssungsmeldung | ✅ Bestanden |
| 7 | Booking-Anfrage ohne Login | Zugriff verweigert / Redirect zu Login | ✅ Bestanden |
| 8 | Booking-Anfrage mit Login, gültigem Datum | Anfrage wird gespeichert, Bestätigung angezeigt | ✅ Bestanden |
| 9 | Booking-Anfrage mit Datum in der Vergangenheit | Fehlermeldung, keine Anfrage gespeichert | ✅ Bestanden |
| 10 | Admin nimmt Anfrage an (kein Konflikt) | Status "accepted", neuer Gig-Eintrag wird automatisch erzeugt | ✅ Bestanden |
| 11 | Admin nimmt Anfrage an, obwohl am selben Datum bereits ein Gig existiert | Annahme wird verweigert, Konflikt-Meldung erscheint | ✅ Bestanden |
| 12 | Normaler User (nicht Admin) ruft `/admin` auf | HTTP 403 Forbidden | ✅ Bestanden |
| 13 | `GET /api/gigs` ohne Authentifizierung | HTTP 200, JSON-Liste der Gigs | ✅ Bestanden |
| 14 | `GET /api/bookings` ohne Token | HTTP 401 Unauthorized | ✅ Bestanden |
| 15 | `GET /api/bookings` mit gültigem Admin-Token | HTTP 200, JSON-Liste der Buchungsanfragen | ✅ Bestanden |

**Hinweis:** Wichtig ist gemäss Aufgabenstellung nicht, dass alle Tests
erfolgreich sind, sondern dass sie definiert und durchgeführt wurden.
Alle 15 Tests waren zum Zeitpunkt der Abgabe erfolgreich (Stand: siehe
`pytest`-Ausgabe im Repository/CI).

## Manuelle Tests (Browser)

| # | Testfall | Erwartetes Ergebnis | Tatsächliches Ergebnis |
|---|----------|----------------------|--------------------------|
| M1 | Registrierung über das Formular im Browser | Weiterleitung zu Login mit Erfolgsmeldung | ✅ Bestanden |
| M2 | Live-Sets-Karussell scrollt automatisch | Karten scrollen sichtbar durch | ✅ Bestanden |
| M3 | Presskit-Links öffnen/downloaden korrekte Dateien | Datei wird geöffnet/heruntergeladen | ✅ Bestanden |
