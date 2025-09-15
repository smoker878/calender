from flask import Blueprint

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

from . import view  # 導入 view 模組，註冊路由
