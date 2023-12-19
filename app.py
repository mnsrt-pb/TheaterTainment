from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, date

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
# db = SQL("sqlite:///theater.db")

# Account Type: staff / user
acc_type = None

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/e-login", methods=["GET", "POST"])
def employee_login():
    """Login associate"""
    return render_template("e-login.html")


@app.route("/e-register", methods=["GET", "POST"])
def employee_register():
    """Register associate"""
    return render_template("e-register.html")


@app.route("/")
# @login_required
def index():
    """Show portfolio of stocks"""
    return apology("TODO", 403)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""
    return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/movies", methods=["GET", "POST"])
def movies():
    """Display available movies"""

    return apology("TODO", 403)


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # Forget any user_id
    session.clear()
    return render_template("register.html")


@app.route("/showtimes", methods=["GET", "POST"])
def shoetimes():
    """Display available movies"""

    return apology("TODO", 403)
