from flask import render_template, request, jsonify
from flask_login import login_required, current_user
from app import db, ma
from app.models import Event
from app.schemes import EventSchema
from datetime import datetime
from flask import jsonify
from marshmallow import ValidationError




from . import calendar_bp

@calendar_bp.route("/")
def index():
    return render_template("calendar/index.html")

# 取得事件，取得自己創造 和 公開的事件 get
@calendar_bp.route("/events")
def get_events():
    if current_user.is_authenticated:
        events = Event.query.filter(
            (Event.user_id == current_user.id) | (Event.is_public == True)
        ).all()
    else:
        events = Event.query.filter_by(is_public=True).all()

    # FullCalendar 需要的欄位
    fc_events = [
        {
            "id": e.id,
            "title": e.title,
            "start": e.start.isoformat(),  # 日期轉成 YYYY-MM-DD
            "end": e.end.isoformat() if e.end else None
        } for e in events
    ]
    return jsonify(fc_events)
    


# 取得事件詳細內容，只能是自己創造 和 公開的事件 get
@calendar_bp.route("/events/<int:event_id>")
def get_events_detail(event_id):
    event = Event.query.get_or_404(event_id)

    if not event.is_public and (not current_user.is_authenticated or event.user_id != current_user.id):
        return jsonify({"error": "無權限查看此事件"}), 403

    event_schema = EventSchema()
    return jsonify(event_schema.dump(event))


    

# 新增事件
@calendar_bp.route("/events", methods=["POST"])
@login_required
def add_event():
    data = request.get_json()
    event_schema = EventSchema()
    try:
        event = event_schema.load(data)
        event.user_id = current_user.id
        db.session.add(event)
        db.session.commit()
        return jsonify(event_schema.dump(event)), 201
    except ValidationError as err:
        return jsonify(err.messages), 400
    
    
# 修改事件，只能是自己創造
@calendar_bp.route("/events/<int:event_id>", methods=["PUT"])
@login_required
def edit_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        return jsonify({"error": "無權限修改此事件"}), 403

    data = request.get_json()
    try:
        # 手動更新欄位
        for key in ["title", "content", "start", "end", "is_public", "group_id"]:
            if key in data:
                setattr(event, key, data[key])

        # 可以用 Marshmallow 來驗證日期
        event_schema = EventSchema()
        event_schema.validate_dates({
            "start": event.start,
            "end": event.end
        })

        db.session.commit()
        return jsonify(event_schema.dump(event))
    except ValidationError as err:
        return jsonify(err.messages), 400
    


# 刪除事件，只能是自己創造
@calendar_bp.route("/events/<int:event_id>", methods=["DELETE"])
@login_required
def delete_event(event_id):
    event = Event.query.get_or_404(event_id)
    if event.user_id != current_user.id:
        return jsonify({"error": "無權限刪除此事件"}), 403

    db.session.delete(event)
    db.session.commit()
    return jsonify({"message": "事件已刪除"})
