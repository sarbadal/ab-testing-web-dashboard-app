import os
from flask import Blueprint

URL_PREFIX = os.getenv('URL_PREFIX', '').rstrip('/')

main_bp = Blueprint('main', __name__, url_prefix=URL_PREFIX if URL_PREFIX else None)