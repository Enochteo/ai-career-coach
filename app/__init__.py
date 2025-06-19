from flask import Flask
from .models import db
from dotenv import load_dotenv
import os
from flask_login import LoginManager
from .models import User

load_dotenv()

# file upload

def create_app():
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///goals.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["UPLOAD_FOLDER"] = os.path.join(app.root_path, "uploads")
    app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024 # max flie is 2 MB
    app.secret_key = "dev"

    db.init_app(app)

    from .routes import main
    app.register_blueprint(main)
    
    with app.app_context():
        db.create_all()


    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)  

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id)) 
    
    from .auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)
    return app

