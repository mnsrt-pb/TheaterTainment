import datetime
from flask import Blueprint, flash, render_template,  redirect, request, url_for
from flask_login import current_user
from theatert import db, bcrypt
from theatert.users.employees.forms import RegistrationForm
from theatert.models import Employee, Change, Movie, Auditorium, Seat, Screening, Ticket
from theatert.users.utils import apology, login_required

import tmdbsimple as tmdb


employees = Blueprint('employees', __name__, url_prefix='/employee')


@employees.route('/auditoriums')
@login_required(role='EMPLOYEE')
def auditoriums():
    page = request.args.get('auditorium', 1, type=int)
    auditorium = Auditorium.query.paginate(page=page, per_page=1)

    for a in auditorium:
        seats = Seat.query.filter_by(auditorium_id = a.id).order_by(Seat.id) 
    
        seats_total = Seat.query.filter(
                            db.and_(
                                Seat.auditorium_id.is_(a.id), 
                                Seat.seat_type.is_not('empty'))).count()

    return render_template('employee/auditoriums.html', auditorium=auditorium, seats=seats, seats_total=seats_total)


# FIXME: add item num for employee changes (0 or add 1 to prev item's num)
# FIXME: should use login_required(role='EMPLOYEE')
@employees.route('/')
@employees.route('/home')
def home():
    '''Show home page'''
    
    if not current_user.is_authenticated:
        return redirect(url_for('users.home'))
    else:
        if current_user.role == 'MEMBER':
            return redirect(url_for('users.home'))

        page = request.args.get('page', 1, type=int)
        type = request.args.get('type', 1, type=int)

        if type == 2:
            data = Change.query.filter_by(employee_id = current_user.id, table_name='movie')\
                .order_by(Change.date.desc())
        elif type == 3:
            data = Change.query.filter_by(employee_id = current_user.id, table_name='screening')\
                .order_by(Change.date.desc())
        else: 
            data = Change.query.filter_by(employee_id = current_user.id)\
                .order_by(Change.date.desc())
        
        total = data.count()
        data = data.paginate(page=page, per_page=10)

        changes = []
        for c in data.items:
            if c.table_name == 'movie':
                temp = {'change' : c.action,
                        'table_name' : 'Movie',
                        'date_time' : c.date - datetime.timedelta(hours=5),
                        'item': Movie.query.filter_by(id = c.data_id).first().title}
                changes.append(temp)
            elif c.table_name == 'screening':
                s = Screening.query.join(Movie).join(Auditorium) \
                    .filter(Screening.id.is_(c.data_id)).first()
                
                seats_total = Seat.query.filter(
                            db.and_(
                                Seat.auditorium_id.is_(s.auditorium.id), 
                                Seat.seat_type.is_not('empty'))).count()

                temp = {'change' : c.action,
                        'table_name' : 'Showtime',
                        'date_time': c.date - datetime.timedelta(hours=5),
                        'item': f'{s.movie.title} | Auditorium {s.auditorium.id} \
                        | {s.start_datetime.strftime("%A, %b %d, %Y")} \
                        | {s.start_datetime.strftime(" %I:%M %p")} \
                        | {seats_total} Tickets'
                }
                changes.append(temp)

    return render_template('employee/home.html', changes=changes, data=data, total=total, type=type)


@employees.route('/register', methods=['GET', 'POST'])
def register():
    '''Register associate'''

    if current_user.is_authenticated:
        if current_user.role == 'EMPLOYEE':
            return redirect(url_for('employees.home'))
        return redirect(url_for('users.home'))

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
        return redirect(url_for('users.employee_login'))
    else:
        return render_template('employee/register.html', form=form)


# TODO: Show which tickets have been purchased and when
@employees.route('/tickets/<int:s_id>', methods=['GET', 'POST'])
@login_required(role='EMPLOYEE')
def tickets(s_id):
    page = request.args.get('page', 1, type=int)

    screening = Screening.query.join(Movie).join(Auditorium) \
        .filter(Screening.id.is_(s_id)) \
        .first_or_404()
    

    tickets = Ticket.query.join(Screening).join(Seat) \
        .filter(Screening.id.is_(s_id)) \
        .order_by(Ticket.id) 
    
    total= tickets.count()

    per_page = 10

    if screening.auditorium.id == 1 or screening.auditorium.id == 2:
        per_page=12

    if screening.auditorium.id == 3:
        per_page=16

    tickets = tickets.paginate(page=page, per_page=per_page)
    return render_template('employee/tickets.html', title='Tickets', screening=screening, tickets=tickets, total=total)

