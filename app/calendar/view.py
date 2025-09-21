from datetime import datetime
from flask import request, jsonify, render_template
from flask.views import MethodView
from flask_login import login_required, current_user
from app import db
from app.models import Event
from app.schemas import EventSchema
from marshmallow import ValidationError
from sqlalchemy import or_
from . import calendar_bp


# 首頁維持原本函式
@calendar_bp.route("/")
def index():
    return render_template("calendar/index.html")


# Event 的 Class-Based View
class EventAPI(MethodView):

    # 取得事件列表或單一事件
    def get(self, event_id=None):
        if event_id is None:
            events = Event.query
            
            start_str = request.args.get("start")
            end_str = request.args.get("end")

            start = datetime.strptime(start_str[:10], "%Y-%m-%d").date() if start_str else None
            end = datetime.strptime(end_str[:10], "%Y-%m-%d").date() if end_str else None                      
            if start:
                events = events.filter(or_(Event.end == None, Event.end >= start))
            if end:
                events = events.filter(Event.start <= end)

            if current_user.is_authenticated:
                events = events.filter(
                    (Event.user_id == current_user.id) | (Event.is_public == True)
                ).all()
            else:
                events = events.filter_by(is_public=True).all()
            

            fc_events = [
                {
                    "id": e.id,
                    "title": f"{e.user.username}:{e.title}",
                    "start": e.start.isoformat(),
                    "end": e.end.isoformat() if e.end else None,
                } for e in events
            ]
            return jsonify(fc_events)
        else:
            # 單一事件詳情
            event = Event.query.get_or_404(event_id)
            if not event.is_public and (not current_user.is_authenticated or event.user_id != current_user.id):
                return jsonify({"error": "無權限查看此事件"}), 403

            event_schema = EventSchema()
            return jsonify(event_schema.dump(event))

    # 新增事件
    @login_required
    def post(self):
        data = request.get_json()
        for key, value in data.items():
            if value == "":
                data[key] = None

        event_schema = EventSchema()
        try:
            event = event_schema.load(data)
            event.user_id = current_user.id
            db.session.add(event)
            db.session.commit()
            return jsonify(event_schema.dump(event)), 201
        except ValidationError as err:
            return jsonify(err.messages), 400

    # 修改事件

    @login_required
    def put(self, event_id):
        event = Event.query.get_or_404(event_id)
        if event.user_id != current_user.id:
            return jsonify({"error": "無權限修改此事件"}), 403

        data = request.get_json()
        try:
            for key in ["title", "content", "start", "end", "is_public", "group_id"]:
                if key in data:
                    value = data[key]

                    # 日期處理
                    if key in ["start", "end"]:
                        if value:  # 有值才轉換
                            value = datetime.strptime(value, "%Y-%m-%d").date()
                        else:
                            value = None  # 空字串 → None

                    setattr(event, key, value)

            # 驗證
            event_schema = EventSchema()
            event_schema.validate_dates({
                "start": event.start,
                "end": event.end
            })

            db.session.commit()
            return jsonify(event_schema.dump(event))

        except ValidationError as err:
            db.session.rollback()
            return jsonify(err.messages), 400
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500


    # 刪除事件
    @login_required
    def delete(self, event_id):
        event = Event.query.get_or_404(event_id)
        if event.user_id != current_user.id:
            return jsonify({"error": "無權限刪除此事件"}), 403

        db.session.delete(event)
        db.session.commit()
        return jsonify({"message": "事件已刪除"})


# 註冊路由
event_view = EventAPI.as_view("event_api")
calendar_bp.add_url_rule("/events/", defaults={"event_id": None}, view_func=event_view, methods=["GET",])
calendar_bp.add_url_rule("/events/", view_func=event_view, methods=["POST",])
calendar_bp.add_url_rule("/events/<int:event_id>", view_func=event_view, methods=["GET", "PUT", "DELETE"])
