from datetime import datetime, timedelta
from flask import Blueprint, flash, render_template,  redirect, request, url_for
from flask_login import current_user, login_user, logout_user
from sqlalchemy import extract
from theatert import bcrypt, db
from theatert.models import Auditorium, Employee, Movie, Screening
from theatert.users.employees.forms import LoginForm
from theatert.users.utils import apology, date_obj


users = Blueprint('users', __name__)


@users.route('/employee/login', methods=['GET', 'POST'])
def employee_login():
    '''Login employee'''

    if current_user.is_authenticated:
        return redirect(url_for('employees.employees.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = Employee.query.filter_by(username=form.username.data).first()

        # Ensure username exists and password is correct
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')

            return redirect(next_page) if next_page else redirect(url_for('employees.home'))
        
        flash('Invalid Username or Password.', 'danger')

    return render_template('/employee/login.html', form=form)


@users.route('/')
def home():
    date = request.args.get('date', default=datetime.today(), type=date_obj)

    movies = Movie.query.filter_by(deleted=False, active=True).order_by(Movie.title)
    dates =[datetime.now() + timedelta(days=x) for x in range(41)]

    showtimes = Screening.query.join(Movie).join(Auditorium) \
        .filter(
            extract('year', Screening.start_datetime)
            ).order_by(Movie.title)

    return render_template('guest/home.html', movies=movies, dates=dates, showtimes=showtimes)


@users.route('/todo')
def todo():
    return apology('TODO', 'member/layout.html', 403)



@users.route('/logout')
def logout():
    '''Log user out'''

    logout_user()

    # Redirect user to login form 
    return redirect(url_for('users.home'))

