from datetime import date

from flask import Blueprint, render_template

from app.models import Gig, SetItem, PressItem

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    upcoming = Gig.query.filter_by(status="upcoming").order_by(Gig.event_date.asc()).all()
    past = Gig.query.filter_by(status="past").order_by(Gig.event_date.desc()).all()
    sets = SetItem.query.order_by(SetItem.created_at.desc()).all()
    press_items = PressItem.query.all()

    return render_template(
        "index.html",
        upcoming=upcoming,
        past=past,
        sets=sets,
        press_items=press_items,
        today=date.today(),
    )
