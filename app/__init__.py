from flask import Flask
from .models import db
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///goals.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.secret_key = "dev"

    db.init_app(app)

    from .routes import main
    app.register_blueprint(main)
    
    with app.app_context():
        db.create_all()
        
    return app