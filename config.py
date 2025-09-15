import os

class Config:
    # Flask 核心設定
    SECRET_KEY = os.environ.get("SECRET_KEY", "default-secret-key")
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"

    # 資料庫
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", "sqlite:///app.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # 郵件服務
    # MAIL_SERVER = os.environ.get("MAIL_SERVER", "localhost")
    # MAIL_PORT = int(os.environ.get("MAIL_PORT", 25))
    # MAIL_USE_TLS = os.environ.get("MAIL_USE_TLS", "false").lower() in ["true", "1"]
    # MAIL_USERNAME = os.environ.get("MAIL_USERNAME")
    # MAIL_PASSWORD = os.environ.get("MAIL_PASSWORD")

class DevelopmentConfig(Config):
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"

class ProductionConfig(Config):
    DEBUG = False

print(os.environ.get("SECRET_KEY"))
