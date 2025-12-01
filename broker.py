from flask import Flask
from routes.user_routes import user_bp
from routes.admin_routes import admin_bp
from routes.desktop_routes import desktop_bp

app = Flask(__name__)
# config.py 에서 SECRET_KEY 및 설정 읽기
app.config.from_object("config")

# 블루프린트 등록 (url_prefix 없이 루트에 매핑)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(desktop_bp)

if __name__ == "__main__":
    # 외부에서도 접속할 수 있도록 0.0.0.0 바인딩
    app.run(host="0.0.0.0", port=5000)

