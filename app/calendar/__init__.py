from flask import Blueprint

calendar_bp = Blueprint("calendar", __name__, url_prefix="/")

from . import view