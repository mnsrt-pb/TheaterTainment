import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv


load_dotenv()

# Configure application
app = Flask(__name__)
app.config['SECRET_KEY'] = '238b73674c2a7a432a1ade61a2ecd214'
app.config["WTF_CSRF_ENABLED"] = False

base_dir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(base_dir, 'theater.db')

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = "danger"


from theatert import routes
