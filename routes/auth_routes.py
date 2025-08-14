# auth_routes.py
from flask import (
    render_template, request, redirect, url_for,
    flash, session
)
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
from services.user_service import get_user_by_username, update_user_password

# ========================
# Decorator to protect routes
# ========================
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("🔒 يجب تسجيل الدخول أولاً", "warning")
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated_function

def register_auth_routes(app):
    @app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            username = request.form["username"].strip()
            password = request.form["password"].strip()
            user = get_user_by_username(username)
            if user and check_password_hash(user["password_hash"], password):
                session["user_id"] = user["user_id"]
                session["username"] = user["username"]
                session["role"] = user["role"]
                flash("✅ تم تسجيل الدخول بنجاح", "success")
                return redirect(url_for("dashboard"))
            else:
                flash("❌ اسم المستخدم أو كلمة المرور غير صحيحة", "danger")
        return render_template("login.html")
    
    @app.route("/logout", methods=["POST"])
    def logout():
        session.clear()
        return redirect(url_for("login"))

    @app.route("/change-password", methods=["GET", "POST"])
    @login_required
    def change_password():
        if request.method == "POST":
            current_password = request.form["current_password"].strip()
            new_password = request.form["new_password"].strip()
            confirm_password = request.form["confirm_password"].strip()
            user = get_user_by_username(session["username"])
            if not check_password_hash(user["password_hash"], current_password):
                flash("❌ كلمة المرور الحالية غير صحيحة", "danger")
                return redirect(url_for("change_password"))
            if new_password != confirm_password:
                flash("❌ كلمة المرور الجديدة غير متطابقة", "danger")
                return redirect(url_for("change_password"))
            new_password_hash = generate_password_hash(new_password)
            update_user_password(user["user_id"], new_password_hash)
            flash("✅ تم تغيير كلمة المرور بنجاح", "success")
            return redirect(url_for("dashboard"))
        return render_template("change_password.html")