# from app import create_app

# app = create_app()

# if __name__ == "__main__":    
#     app.run(debug=True)


from app import create_app

# 根據環境選擇設定，預設使用開發環境
import os
env = os.environ.get("FLASK_ENV", "development")

if env == "production":
    app = create_app("production")
else:
    app = create_app("development")

if __name__ == "__main__":
    app.run(debug=True)