from datetime import timedelta
from flask import Flask
import os

from .routes import main_url, index, dashboard, login, logout, make_session
from .users import ensure_user_store

SESSION_TIME = int(os.getenv("SESSION_TIME", 1))

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)
app.secret_key = os.getenv("APP_SECRET", "51HgZrX9Q2bYlX3sYvPqL9aTgZrX9Q2b")
app.permanent_session_lifetime = timedelta(minutes=SESSION_TIME) 


def create_app():
    ensure_user_store()
    main_url.main_bp.register_blueprint(make_session.bp)
    main_url.main_bp.register_blueprint(index.bp)
    main_url.main_bp.register_blueprint(dashboard.bp)
    main_url.main_bp.register_blueprint(login.bp)
    main_url.main_bp.register_blueprint(logout.bp)
    app.register_blueprint(main_url.main_bp)
    return app