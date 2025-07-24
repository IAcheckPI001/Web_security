from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from .config_database import Config_database


db = SQLAlchemy()
app = Flask(__name__,template_folder="../frontend/templates",static_folder="../frontend/assets")


def create_app():

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    
    # config_dt = Config_database('hjshjhdjah kjshkjdhjs', 'mssql+pyodbc://syscus02:cus123#@muadonglanhleo\MIX/AIShop?driver=SQL+Server', False) # Used for MSSQL
    config_dt = Config_database('hjshjhdjah kjshkjdhjs', 'postgresql://syscus02:cus123#@localhost:5432/AIShop', False)  # Used for PostgreSQL   

    app.config.from_object(config_dt)
    

    db.init_app(app)
    from .models import User
    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader

    def load_user(email):
        return User.query.filter_by(email=email).first()

    

    return app

def set_permission(key, uri):

    db.session.close_all()
    db.session.remove()
    app.config.update(SECRET_KEY=key)
    app.config.update(SQLALCHEMY_DATABASE_URI=uri)
    app.config.update(SQLALCHEMY_TRACK_MODIFICATIONS=False)

