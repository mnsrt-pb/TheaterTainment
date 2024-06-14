from flask import Flask
from flask_bcrypt import Bcrypt
from flask_qrcode import QRcode
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv

import os


load_dotenv()


# Create extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()


# Get employee key
base_dir = os.path.abspath(os.path.dirname(__file__))
employee_key = os.environ.get('EMPLOYEE_KEY')


# login_manager.login_view = 'users.member_login'
login_manager.blueprint_login_views = {
    'members': 'users.member_login',
    'employees': 'users.employee_login',
}
login_manager.login_message_category = "custom"


def create_app(Config):
    # Configure application
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    QRcode(app)

    # Blueprints
    from theatert.users.employees.routes import employees
    from theatert.users.members.routes import members
    from theatert.users.routes import users
    from theatert.errors.handlers import errors


    app.register_blueprint(employees)
    app.register_blueprint(members)
    app.register_blueprint(users)
    app.register_blueprint(errors)

    return app

