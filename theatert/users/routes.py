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


# TODO: Ensure only users who are not logged in can get here
@users.route('/')
def home():
    date = request.args.get('date', default=datetime.today(), type=date_obj)
    max_days = 41
    date if date <= datetime.today() + timedelta(days=max_days) else datetime.today()

    movies = Movie.query.filter_by(deleted=False, active=True).order_by(Movie.title)
    dates =[datetime.today() + timedelta(days=x) for x in range(max_days)]

    # movies with showtimes for given date
    m_showtimes = Screening.query.join(Movie).join(Auditorium) \
        .filter(
            db.and_(
                extract('year', Screening.start_datetime).is_(date.year),
                extract('month', Screening.start_datetime).is_(date.month),
                extract('day', Screening.start_datetime).is_(date.day),
            )).group_by(Screening.movie_id).order_by(Movie.title)
    
    # showtimes for each movie
    s_showtimes = []
    for s in m_showtimes:
        st = Screening.query.join(Movie).join(Auditorium) \
        .filter(
            db.and_(
                Screening.movie_id.is_(s.movie_id),
                extract('year', Screening.start_datetime).is_(date.year),
                extract('month', Screening.start_datetime).is_(date.month),
                extract('day', Screening.start_datetime).is_(date.day),
            )).order_by(Screening.start_datetime)
        s_showtimes.append(st)

    return render_template('guest/home.html', movies=movies, dates=dates, m_showtimes=m_showtimes, s_showtimes=s_showtimes)


@users.route('/movies/<string:movie_route>')
def movie(movie_route):
    '''Display movie info like it'll be displayed to members/guests.'''
    date = request.args.get('date', default=datetime.today(), type=date_obj)
    max_days = 12
    date if date <= datetime.today() + timedelta(days=max_days) else datetime.today()

    movie = Movie.query.filter_by(route = movie_route, deleted=False, active=True).first_or_404()
    dates =[datetime.now() + timedelta(days=x) for x in range(max_days)]

    showtimes = Screening.query.join(Movie).join(Auditorium) \
    .filter(
        db.and_(
            Screening.movie_id.is_(movie.id),
            extract('year', Screening.start_datetime).is_(date.year),
            extract('month', Screening.start_datetime).is_(date.month),
            extract('day', Screening.start_datetime).is_(date.day),
        )).order_by(Screening.start_datetime)

    return render_template('member/movie.html', ext="member/layout.html", Movie=movie, dates=dates, Showtimes=showtimes)



@users.route('/logout')
def logout():
    '''Log user out'''

    logout_user()

    # Redirect user to login form 
    return redirect(url_for('users.home'))


@users.route('/todo')
def todo():
    return apology('TODO', 'member/layout.html', 403)

