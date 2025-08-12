# custody_routes.py
from flask import (
    render_template, redirect, url_for,
    session, abort
)
from services.user_service import get_all_users
from services.custody_service import get_custody_by_user_id

def register_custody_routes(app):
    @app.route("/custodies")
    def custodies():
        if "user_id" not in session:
            return redirect(url_for("login"))
        role = session.get("role")
        if role in ["admin", "accountant"]:
            users = get_all_users(exclude_roles=["accountant", "admin"])
            return render_template("custodies_list.html", users=users)
        return redirect(url_for("custody_detail", user_id=session["user_id"]))

    @app.route("/custody/<int:user_id>")
    def custody_detail(user_id):
        if "user_id" not in session:
            return redirect(url_for("login"))
        role = session.get("role")
        current_user_id = session["user_id"]
        if role not in ["admin", "accountant"] and current_user_id != user_id:
            abort(403)
        custody_data = get_custody_by_user_id(user_id)
        return render_template("custody_detail.html", custody_data=custody_data)