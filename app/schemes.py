from app import ma
from marshmallow import fields
from .models import User, Event, Group

class EventSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Event
        include_fk = True
        load_instance = True

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
