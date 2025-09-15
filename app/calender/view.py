from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from app import db
from app.models import Event
from datetime import datetime

from . import calendar_bp

@calendar_bp.route("/")
def index():
    return render_template("calendar/index.html")

# 取得事件 (給 FullCalendar)
@calendar_bp.route("/events")
@login_required
def get_events():
    events = Event.query.filter_by(user_id=current_user.id).all()
    data = [
        {
            "id": e.id,
            "title": e.title,
            "start": e.start.isoformat(),
            "end": e.end.isoformat() if e.end else e.start.isoformat(),
        }
        for e in events
    ]
    return jsonify(data)

# 新增事件
@calendar_bp.route("/events", methods=["POST"])
@login_required
def add_event():
    data = request.get_json()
    title = data.get("title")
    content = data.get("content")
    start = data.get("start")
    end = data.get("end")

    if not title or not start:
        return jsonify({"error": "title and start date required"}), 400

    event = Event(
        user_id=current_user.id,
        title=title,
        content=content,
        start=datetime.fromisoformat(start).date(),
        end=datetime.fromisoformat(end).date() if end else None,
    )
    db.session.add(event)
    db.session.commit()

    return jsonify({"message": "event created", "id": event.id})
