from app import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from app import login_manager
from app.BaseModel import BaseModel

class User(UserMixin, db.Model, BaseModel):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    events = db.relationship("Event", back_populates="user", cascade="all, delete-orphan")
    groups = db.relationship("Group",secondary="user_groups",back_populates="users")
    

    def set_password(self, password):
        """將密碼加密存入資料庫"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """驗證密碼是否正確"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class Event(db.Model, BaseModel):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey("groups.id"), nullable=True)
    is_public = db.Column(db.Boolean, default=False, nullable=False)
    title = db.Column(db.String(128), nullable=False)
    content = db.Column(db.String(350), nullable=True)
    start = db.Column(db.Date, nullable=False)
    end = db.Column(db.Date, nullable=True)
    
    user = db.relationship("User", back_populates="events")
    group = db.relationship("Group", back_populates="events")


    def __repr__(self):
        return f"<Event {self.title} ({self.start} - {self.end})>"
    

class Group(db.Model, BaseModel):
    __tablename__ = "groups"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), unique=True, nullable=False)
    events = db.relationship("Event", back_populates="group", cascade="all, delete-orphan")
    users = db.relationship("User", secondary="user_groups", back_populates="groups")
    def __repr__(self):
        return f"<Group {self.name}>"
    
user_groups = db.Table(
    "user_groups",
    db.Column("user_id", db.Integer, db.ForeignKey("users.id"), primary_key=True),
    db.Column("group_id", db.Integer, db.ForeignKey("groups.id"), primary_key=True)
)