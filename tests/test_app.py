"""
Automatisierte Tests fuer die wichtigsten Anforderungen der Praxisarbeit:
Registrierung, Login, Booking-Workflow (inkl. Konfliktpruefung) und API.

Aufruf:  pytest -v
"""
import os
import tempfile
from datetime import date, timedelta

import pytest

os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from app import create_app
from app.extensions import db
from app.models import User, Gig


@pytest.fixture
def app():
    app = create_app()
    app.config.update(TESTING=True, WTF_CSRF_ENABLED=False)
    with app.app_context():
        db.drop_all()
        db.create_all()
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


def register(client, username="testuser", email="test@example.com", password="secret123"):
    return client.post("/register", data={
        "username": username, "email": email, "password": password
    }, follow_redirects=True)


def login(client, username="testuser", password="secret123"):
    return client.post("/login", data={
        "username": username, "password": password
    }, follow_redirects=True)


def test_homepage_loads(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert b"KEV" in resp.data


def test_registration_creates_user(client, app):
    register(client)
    with app.app_context():
        assert User.query.filter_by(username="testuser").count() == 1


def test_first_registered_user_becomes_admin(client, app):
    register(client)
    with app.app_context():
        user = User.query.filter_by(username="testuser").first()
        assert user.is_admin is True
        assert user.api_token is not None


def test_duplicate_username_rejected(client):
    register(client, username="dupe", email="a@example.com")
    resp = register(client, username="dupe", email="b@example.com")
    assert b"bereits vergeben" in resp.data


def test_login_wrong_password_rejected(client):
    register(client)
    resp = login(client, password="wrongpassword")
    assert b"falsch" in resp.data


def test_login_success(client):
    register(client)
    resp = login(client)
    assert b"Willkommen" in resp.data


def test_booking_requires_login(client):
    resp = client.post("/booking/request", data={
        "event_date": (date.today() + timedelta(days=10)).isoformat(),
        "location": "Test Club",
        "message": "Test",
    }, follow_redirects=True)
    # redirect zu login, da @login_required
    assert b"Login" in resp.data or resp.status_code == 200


def test_logged_in_user_can_submit_booking(client, app):
    register(client)
    login(client)
    resp = client.post("/booking/request", data={
        "event_date": (date.today() + timedelta(days=10)).isoformat(),
        "location": "Test Club",
        "message": "Test Anfrage",
    }, follow_redirects=True)
    assert b"versendet" in resp.data


def test_booking_rejects_past_date(client):
    register(client)
    login(client)
    resp = client.post("/booking/request", data={
        "event_date": (date.today() - timedelta(days=5)).isoformat(),
        "location": "Test Club",
        "message": "Test",
    }, follow_redirects=True)
    assert b"Vergangenheit" in resp.data


def test_admin_can_accept_booking_and_gig_is_created(client, app):
    register(client)  # wird automatisch admin
    login(client)
    client.post("/booking/request", data={
        "event_date": (date.today() + timedelta(days=20)).isoformat(),
        "location": "Konflikt-Club",
        "message": "x",
    })
    with app.app_context():
        from app.models import BookingRequest
        booking = BookingRequest.query.first()
        booking_id = booking.id

    resp = client.post(f"/admin/bookings/{booking_id}/accept", follow_redirects=True)
    assert b"angenommen" in resp.data
    with app.app_context():
        assert Gig.query.filter_by(city="Konflikt-Club").count() == 1


def test_booking_conflict_detection(client, app):
    register(client)  # admin
    login(client)
    event_date = (date.today() + timedelta(days=30)).isoformat()

    with app.app_context():
        db.session.add(Gig(venue="Existing Gig", city="Zurich", event_date=date.today() + timedelta(days=30),
                            status="upcoming"))
        db.session.commit()

    client.post("/booking/request", data={"event_date": event_date, "location": "New Club", "message": "x"})
    with app.app_context():
        from app.models import BookingRequest
        booking_id = BookingRequest.query.first().id

    resp = client.post(f"/admin/bookings/{booking_id}/accept", follow_redirects=True)
    assert b"Konflikt" in resp.data


def test_non_admin_cannot_access_dashboard(client):
    register(client, username="admin1", email="admin1@example.com")   # wird admin
    register(client, username="user2", email="user2@example.com")     # normaler user
    login(client, username="user2")
    resp = client.get("/admin")
    assert resp.status_code == 403


def test_api_gigs_public_and_returns_json(client, app):
    with app.app_context():
        db.session.add(Gig(venue="API Test Gig", city="Bern", event_date=date.today(), status="upcoming"))
        db.session.commit()
    resp = client.get("/api/gigs")
    assert resp.status_code == 200
    data = resp.get_json()
    assert any(g["venue"] == "API Test Gig" for g in data)


def test_api_bookings_requires_token(client):
    resp = client.get("/api/bookings")
    assert resp.status_code == 401


def test_api_bookings_with_valid_admin_token(client, app):
    register(client)  # admin, hat automatisch Token
    with app.app_context():
        token = User.query.first().api_token
    resp = client.get("/api/bookings", headers={"Authorization": f"Bearer {token}"})
    assert resp.status_code == 200
