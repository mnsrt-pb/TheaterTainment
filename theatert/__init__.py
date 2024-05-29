from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
from theatert.config import Config


load_dotenv()

# Create extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
login_manager = LoginManager()

# login_manager.login_view = 'users.member_login'
login_manager.blueprint_login_views = {
    'members': 'users.member_login',
    'employees': 'users.employee_login',
}
login_manager.login_message_category = "light"


def create_app(config_class=Config):
    # Configure application
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)

    # Blueprints
    from theatert.users.employees.movies.routes import movies
    from theatert.users.employees.showtimes.routes import showtimes
    from theatert.users.employees.routes import employees
    from theatert.users.members.routes import members
    from theatert.users.routes import users
    employees.register_blueprint(movies)
    employees.register_blueprint(showtimes)
    app.register_blueprint(employees)
    app.register_blueprint(members)
    app.register_blueprint(users)

    return app

