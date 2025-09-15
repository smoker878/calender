from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from . import auth_bp
from app.models import User
from app import db

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("calendar.index"))

    email = ""
    remember = False

    if request.method == "POST":
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        remember = bool(request.form.get("remember"))

        if not email or not password:
            flash("請填寫所有欄位", "danger")
            # 保留 email
            return render_template("auth/login.html", email=email, remember=remember)

        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user, remember=remember)
            flash("登入成功！", "success")
            next_page = request.args.get("next")
            return redirect(next_page or url_for("main.index"))
        else:
            flash("帳號或密碼錯誤", "danger")
            return render_template("auth/login.html", email=email, remember=remember)

    return render_template("auth/login.html", email=email, remember=remember)


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("calendar.index"))

    username = ""
    email = ""

    if request.method == "POST":
        username = request.form.get("username", "")
        email = request.form.get("email", "")
        password = request.form.get("password", "")
        password1 = request.form.get("password1", "")

        if not username or not email or not password:
            flash("請填寫所有欄位", "danger")
            return render_template("auth/register.html", username=username, email=email)

        if User.query.filter_by(email=email).first():
            flash("此 Email 已被註冊", "warning")
            return render_template("auth/register.html", username=username, email=email)
        
        if password != password1:
            flash("兩次輸入密碼不相同")
            return redirect(url_for("auth.register"))

        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        flash("註冊成功，請登入！", "success")
        return redirect(url_for("auth.login"))

    return render_template("auth/register.html", username=username, email=email)

@auth_bp.route("/logout")
@login_required
def logout():
    logout_user()  # 清掉 session 中的登入資訊
    return redirect(url_for("calendar.index"))





