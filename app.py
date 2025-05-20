from flask import Flask
from db import init_db
from routes.auth import auth_bp
from routes.shop import shop_bp
from routes.recommend import recommend_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = 'your-secret-key'

    init_db()

    app.register_blueprint(auth_bp)
    app.register_blueprint(shop_bp)
    app.register_blueprint(recommend_bp)
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)