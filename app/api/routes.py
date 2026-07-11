"""
Hinweis zur Quellenverwendung (gemaess Leitfaden fuer schriftliche Arbeiten
der ipso! Bildung, Kap. 2.1.3): Das REST-API inkl. Token-Authentifizierung
in diesem Modul wurde in Zusammenarbeit mit dem KI-Werkzeug Claude
(Anthropic) entwickelt. Pruefung, Anpassung und inhaltliche Verantwortung
liegen beim Verfasser (Kevin Martinez). Vollstaendige Deklaration siehe
KI-Deklarationstabelle in der Eigenstaendigkeitserklaerung der
schriftlichen Dokumentation.
"""
from functools import wraps

from flask import Blueprint, jsonify, request

from app.models import Gig, SetItem, User, BookingRequest

api_bp = Blueprint("api", __name__)


def token_required(view_func):
    """
    Prueft den Header 'Authorization: Bearer <token>' gegen die
    api_token-Spalte eines Users. Funktioniert ohne Browser, z.B.:
      curl -H "Authorization: Bearer <token>" https://host/api/bookings
    Wird fuer Endpunkte verwendet, die nicht-oeffentliche Daten liefern
    (hier: Booking-Anfragen, nur fuer Admins bestimmt).
    """
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"error": "Missing or malformed Authorization header"}), 401

        token = auth_header.split(" ", 1)[1].strip()
        user = User.query.filter_by(api_token=token).first()
        if not user or not user.is_admin:
            return jsonify({"error": "Invalid or unauthorized token"}), 401

        return view_func(*args, **kwargs)
    return wrapped


# ---------------------------------------------------------------------------
# Oeffentliche, lesende Endpunkte (kein Login noetig - nur Gigs/Sets-Daten,
# die ohnehin auf der Webseite oeffentlich sichtbar sind)
# ---------------------------------------------------------------------------

@api_bp.route("/gigs", methods=["GET"])
def get_gigs():
    """GET /api/gigs?status=upcoming|past (optional)"""
    status = request.args.get("status")
    query = Gig.query
    if status in ("upcoming", "past", "cancelled"):
        query = query.filter_by(status=status)
    gigs = query.order_by(Gig.event_date.asc()).all()
    return jsonify([g.to_dict() for g in gigs])


@api_bp.route("/gigs/<int:gig_id>", methods=["GET"])
def get_gig(gig_id):
    gig = Gig.query.get_or_404(gig_id)
    return jsonify(gig.to_dict())


@api_bp.route("/sets", methods=["GET"])
def get_sets():
    sets = SetItem.query.order_by(SetItem.created_at.desc()).all()
    return jsonify([s.to_dict() for s in sets])


# ---------------------------------------------------------------------------
# Geschuetzter Endpunkt: Booking-Anfragen sind nicht oeffentlich, daher
# Token-Pflicht. Erfuellt die Anforderung "Authentifizierung des Clients
# am API muss ebenfalls ohne Browser moeglich sein".
# ---------------------------------------------------------------------------

@api_bp.route("/bookings", methods=["GET"])
@token_required
def get_bookings():
    """GET /api/bookings  (Header: Authorization: Bearer <token>)"""
    status = request.args.get("status")
    query = BookingRequest.query
    if status in ("pending", "accepted", "declined"):
        query = query.filter_by(status=status)
    bookings = query.order_by(BookingRequest.created_at.desc()).all()
    return jsonify([b.to_dict() for b in bookings])
