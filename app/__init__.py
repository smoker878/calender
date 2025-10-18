from flask import Flask, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_marshmallow import Marshmallow
from config import DevelopmentConfig, ProductionConfig
import os


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
login_manager.login_view = "auth.login"
ma = Marshmallow()


def create_app(config_name="development"):
    app = Flask(__name__)

    # 設定
    if config_name == "production":
        app.config.from_object(ProductionConfig)
    else:
        app.config.from_object(DevelopmentConfig)

    # ✅ 從環境變數取得上傳資料夾
    app.config["UPLOAD_FOLDER"] = os.getenv("UPLOAD_FOLDER", "./uploads")
    os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
    
    @app.route("/uploads/<path:filename>")
    def uploaded_file(filename):
        # 將 UPLOAD_FOLDER 轉成絕對路徑
        upload_dir = os.path.abspath(app.config["UPLOAD_FOLDER"])
        full_path = os.path.join(upload_dir, filename)
        # print("Looking for:", full_path)
        # 使用 send_from_directory 提供檔案
        return send_from_directory(upload_dir, filename)


    # 初始化擴展
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)

    ma.init_app(app)

    # 藍圖
    from .auth.view import auth_bp
    app.register_blueprint(auth_bp)
    from .calendar.view  import calendar_bp
    app.register_blueprint(calendar_bp)
    from .upload.view import upload_bp
    app.register_blueprint(upload_bp)





    return app