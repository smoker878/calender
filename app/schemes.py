from app import ma
from marshmallow import fields, validates_schema, ValidationError
from .models import User, Event, Group

class EventSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Event
        include_fk = True
        load_instance = True
    @validates_schema
    def validate_dates(self, data, **kwargs):
        start = data.get("start")
        end = data.get("end")
        if end and start and end < start:
            raise ValidationError("結束日期不能小於開始日期", field_name="end")

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = User
        include_relationships = True
        load_instance = True

    events = fields.Nested(EventSchema, many=True)

class GroupSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Group
        include_relationships = True
        load_instance = True

    users = fields.Nested(UserSchema, many=True)
