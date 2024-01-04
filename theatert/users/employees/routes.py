import datetime
from flask import Blueprint, flash, render_template,  redirect, request, url_for
from flask_login import current_user
from theatert import db, bcrypt
from theatert.users.employees.forms import RegistrationForm
from theatert.models import Employee, Change, Movie
from theatert.users.utils import apology, login_required

import tmdbsimple as tmdb


employees = Blueprint('employees', __name__, url_prefix='/employee')


@employees.route('/add-showtime', methods=['GET', 'POST'])
@login_required(role="EMPLOYEE")
def add_showtime():
    '''Assign showtimes to movies'''

    return apology('TODO', 'employee/layout.html', 403)


@employees.route('/')
@employees.route('/home')
def home():
    '''Show home page'''
    
    # FIXME: should be something else
    if not current_user.is_authenticated:
        return apology('TODO', 'member/layout.html', 403)
    else:
        page = request.args.get('page', 1, type=int)
        data = Change.query.filter_by(employee_id = current_user.id)\
            .order_by(Change.date.desc())\
            .paginate(page=page, per_page=10)
        
        changes = []
        for c in data.items:
            if c.table_name == 'movie':
                temp = {'change' : c.action,
                        'table_name' : 'Movie',
                        'date_time' : c.date - datetime.timedelta(hours=5),
                        'item': Movie.query.filter_by(id = c.data_id).first().title}
                changes.append(temp)

    return render_template('employee/home.html', changes=changes, data=data)


@employees.route('/register', methods=['GET', 'POST'])
def register():
    '''Register associate'''

    if current_user.is_authenticated:
        return redirect(url_for('employees.home'))

    form = RegistrationForm()
    if form.validate_on_submit():
        # Insert a new user to database
        user = Employee(
            username = form.username.data,
            password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        )
        db.session.add(user)
        db.session.commit()

        flash('Your account has been created! You are now able to log in.', 'success')
        return redirect(url_for('employees.login'))
    else:
        return render_template('employee/register.html', form=form)

