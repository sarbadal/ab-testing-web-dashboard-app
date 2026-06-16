from flask import Blueprint, render_template, request, session, redirect, url_for
from app.users import authenticate_user

bp = Blueprint("login", __name__)

@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        user = authenticate_user(username, password)

        if user:
            session["logged_in"] = True
            session["username"] = username
            session["is_admin"] = bool(user.get("is_admin", False))
            return redirect(url_for("main.index.index"))
        return render_template("password_incorrect.html")
    return render_template("password_form.html")