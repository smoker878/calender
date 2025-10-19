# from flask import current_app
from app import ma
from marshmallow import fields, validates_schema, ValidationError
from .models import User, Event, Group, EventImage

class EventImageSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = EventImage
        load_instance = True
        exclude = ("event_id",)

    # url = fields.Method("get_image_url")

    # def get_image_url(self, obj):
    #     """依照 filename 動態產生圖片 URL"""
    #     if not obj.filename:
    #         return None
    #     upload_root = current_app.config["UPLOAD_FOLDER"]
    #     return f"{upload_root}/{obj.filename}"
 

class EventSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Event
        include_fk = True
        load_instance = True
    user_id = fields.Int(dump_only=True)
    username = fields.Function(lambda obj: obj.user.username if obj.user else None)
    end = fields.Date(allow_none=True)
    images = fields.Nested(EventImageSchema, many=True)
    # images = fields.List(fields.Str())

    @validates_schema
    def validate_dates(self, data, **kwargs):
        start = data.get("start")
        end = data.get("end")
        if end and start and end < start:
            raise ValidationError("結束日期不能小於開始日期", field_name="end")
        elif end == start:
            data["end"] = None


class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True

    events = fields.Nested(EventSchema, many=True)


class UserSearchSchema(ma.SQLAlchemySchema):
    class Meta:
        model = User

    id = fields.Int()
    username = fields.Str()

class GroupSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Group
        include_relationships = True
        load_instance = True

    users = fields.Nested("UserSchema", many=True, only=("id", "username"))
    events = fields.Nested("EventSchema", many=True, only=("id", "title", "start", "end"))
    user_count = fields.Method("get_user_count")
    event_count = fields.Method("get_event_count")

    def get_user_count(self, obj):
        return len(obj.users)

    def get_event_count(self, obj):
        return len(obj.events)
