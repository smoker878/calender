from flask import Blueprint

upload_bp = Blueprint("upload", __name__, url_prefix="/upload")

from . import view