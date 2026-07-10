from datetime import datetime
from functools import wraps

from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_required, current_user

from app.extensions import db
from app.models import BookingRequest, Gig, SetItem, PressItem

booking_bp = Blueprint("booking", __name__)


def admin_required(view_func):
    """Decorator: nur eingeloggte Admin-User duerfen auf die View zugreifen."""
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return view_func(*args, **kwargs)
    return wrapped


# ---------------------------------------------------------------------------
# Oeffentlicher Teil: Booking-Anfrage stellen (Login erforderlich)
# ---------------------------------------------------------------------------

@booking_bp.route("/booking/request", methods=["POST"])
@login_required
def create_booking():
    event_date_str = request.form.get("event_date", "")
    location = request.form.get("location", "").strip()
    message = request.form.get("message", "").strip()

    try:
        event_date = datetime.strptime(event_date_str, "%Y-%m-%d").date()
    except ValueError:
        flash("Bitte ein gueltiges Datum angeben.", "error")
        return redirect(url_for("main.index") + "#booking")

    if event_date < datetime.utcnow().date():
        flash("Das Event-Datum darf nicht in der Vergangenheit liegen.", "error")
        return redirect(url_for("main.index") + "#booking")

    booking = BookingRequest(
        requester_id=current_user.id,
        requester_name=current_user.username,
        requester_email=current_user.email,
        event_date=event_date,
        location=location,
        message=message,
        status="pending",
    )
    db.session.add(booking)
    db.session.commit()

    flash("Deine Booking-Anfrage wurde versendet. Danke!", "success")
    return redirect(url_for("main.index") + "#booking")


# ---------------------------------------------------------------------------
# Admin-Bereich
# ---------------------------------------------------------------------------

@booking_bp.route("/admin")
@login_required
@admin_required
def dashboard():
    bookings = BookingRequest.query.order_by(BookingRequest.created_at.desc()).all()
    gigs = Gig.query.order_by(Gig.event_date.desc()).all()
    sets = SetItem.query.order_by(SetItem.created_at.desc()).all()
    press_items = PressItem.query.all()
    return render_template(
        "admin/dashboard.html", bookings=bookings, gigs=gigs, sets=sets, press_items=press_items
    )


@booking_bp.route("/admin/bookings/<int:booking_id>/accept", methods=["POST"])
@login_required
@admin_required
def accept_booking(booking_id):
    """
    Geschaeftslogik: eine Anfrage kann nur angenommen werden, wenn am
    selben Datum noch kein anderer (nicht abgesagter) Gig existiert.
    Beim Annehmen wird automatisch ein Gig-Eintrag erzeugt.
    """
    booking = BookingRequest.query.get_or_404(booking_id)

    if booking.status != "pending":
        flash("Diese Anfrage wurde bereits bearbeitet.", "error")
        return redirect(url_for("booking.dashboard"))

    conflict = Gig.query.filter(
        Gig.event_date == booking.event_date, Gig.status != "cancelled"
    ).first()
    if conflict:
        flash(
            f"Konflikt: Am {booking.event_date} existiert bereits ein Gig "
            f"({conflict.venue}). Anfrage kann nicht angenommen werden, "
            f"solange dieser Konflikt besteht.",
            "error",
        )
        return redirect(url_for("booking.dashboard"))

    booking.status = "accepted"
    new_gig = Gig(
        venue=booking.location or "TBA",
        city=booking.location or "TBA",
        tag="Booking",
        event_date=booking.event_date,
        status="upcoming",
        created_by_id=current_user.id,
    )
    db.session.add(new_gig)
    db.session.commit()

    flash("Anfrage angenommen, Gig wurde automatisch angelegt.", "success")
    return redirect(url_for("booking.dashboard"))


@booking_bp.route("/admin/bookings/<int:booking_id>/decline", methods=["POST"])
@login_required
@admin_required
def decline_booking(booking_id):
    booking = BookingRequest.query.get_or_404(booking_id)
    if booking.status != "pending":
        flash("Diese Anfrage wurde bereits bearbeitet.", "error")
        return redirect(url_for("booking.dashboard"))

    booking.status = "declined"
    db.session.commit()
    flash("Anfrage abgelehnt.", "info")
    return redirect(url_for("booking.dashboard"))


@booking_bp.route("/admin/gigs/add", methods=["POST"])
@login_required
@admin_required
def add_gig():
    try:
        event_date = datetime.strptime(request.form.get("event_date", ""), "%Y-%m-%d").date()
    except ValueError:
        flash("Ungueltiges Datum.", "error")
        return redirect(url_for("booking.dashboard"))

    status = "upcoming" if event_date >= datetime.utcnow().date() else "past"

    gig = Gig(
        venue=request.form.get("venue", "").strip(),
        city=request.form.get("city", "").strip(),
        tag=request.form.get("tag", "").strip(),
        event_date=event_date,
        status=status,
        created_by_id=current_user.id,
    )
    db.session.add(gig)
    db.session.commit()
    flash("Gig hinzugefuegt.", "success")
    return redirect(url_for("booking.dashboard"))


@booking_bp.route("/admin/gigs/<int:gig_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_gig(gig_id):
    gig = Gig.query.get_or_404(gig_id)
    db.session.delete(gig)
    db.session.commit()
    flash("Gig geloescht.", "info")
    return redirect(url_for("booking.dashboard"))


@booking_bp.route("/admin/sets/add", methods=["POST"])
@login_required
@admin_required
def add_set():
    s = SetItem(
        title=request.form.get("title", "").strip(),
        platform=request.form.get("platform", "youtube"),
        video_id=request.form.get("video_id", "").strip(),
        thumb_url=request.form.get("thumb_url", "").strip(),
        external_url=request.form.get("external_url", "").strip(),
    )
    db.session.add(s)
    db.session.commit()
    flash("Set hinzugefuegt.", "success")
    return redirect(url_for("booking.dashboard"))


@booking_bp.route("/admin/sets/<int:set_id>/delete", methods=["POST"])
@login_required
@admin_required
def delete_set(set_id):
    s = SetItem.query.get_or_404(set_id)
    db.session.delete(s)
    db.session.commit()
    flash("Set geloescht.", "info")
    return redirect(url_for("booking.dashboard"))
