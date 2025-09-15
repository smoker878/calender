from flask import Blueprint, render_template, request
from .models import User

main_bp = Blueprint("main", __name__)

@main_bp.route("/")
def index():
    return render_template("index.html")

@main_bp.route("/hello/<name>")
def hello(name):
    return f"Hello, {name}!"

@main_bp.route("/user", methods=["POST"])
def add_user():
    username = request.form.get("username")
    # 假設有 User model
    user = User(username=username)
    # db.session.add(user)
    # db.session.commit()
    return f"User {username} added!"
