import datetime
from flask import Blueprint, flash, render_template,  redirect, request, url_for
from flask_login import current_user
from theatert import db, bcrypt
from theatert.users.employees.forms import RegistrationForm
from theatert.models import Auditorium, Change, Employee, Movie, Purchase, Purchased_Ticket, Seat, Screening, Ticket
from theatert.users.utils import apology, guest, login_required

from pytz import timezone, utc
tz = timezone('US/Eastern')

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


@employees.route('/')
@login_required(role='EMPLOYEE')
def home():
    '''Show home page'''

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
                dt = utc.localize(c.date)
                temp = {'change' : c.action,
                        'table_name' : 'Movie',
                        'date_time' : dt.astimezone(tz),
                        'item': Movie.query.filter_by(id = c.data_id).first().title}
                changes.append(temp)
            elif c.table_name == 'screening':
                s = Screening.query.join(Movie).join(Auditorium) \
                    .filter(Screening.id.is_(c.data_id)).first()
                
                seats_total = Seat.query.filter(
                            db.and_(
                                Seat.auditorium_id.is_(s.auditorium.id), 
                                Seat.seat_type.is_not('empty'))).count()

                dt = utc.localize(c.date)
                temp = {'change' : c.action,
                        'table_name' : 'Showtime',
                        'date_time': dt.astimezone(tz),
                        'item': f'{s.movie.title} | Auditorium {s.auditorium.id} \
                        | {s.start_datetime.strftime("%A, %b %d, %Y")} \
                        | {s.start_datetime.strftime(" %I:%M %p")} \
                        | {seats_total} Tickets'
                }
                changes.append(temp)

    return render_template('employee/home.html', changes=changes, data=data, total=total, type=type)


@employees.route('/purchase-info/<string:confirmation>')
@login_required(role='EMPLOYEE')
def purchase_info(confirmation):
    tickets = Purchased_Ticket.query.join(Ticket).join(Purchase).join(Seat)\
        .filter(
            db.and_(Purchase.confirmation.is_(confirmation),
                    Purchased_Ticket.purchase_id.is_(Purchase.id),
                    Ticket.id.is_(Purchased_Ticket.ticket_id),
                    Seat.id.is_(Ticket.seat_id)))
    
    purchase = tickets.first_or_404().purchase

    screening = Screening.query.join(Movie).join(Auditorium) \
        .filter(Screening.id.is_(tickets.first().ticket.screening_id)).first()
        

    return render_template('/employee/purchase-info.html', purchase=purchase, tickets=tickets, screening=screening, total=tickets.count())


@employees.route('/register', methods=['GET', 'POST'])
@guest()
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

        flash('Your account has been created! You are now able to log in.', 'light')
        return redirect(url_for('users.employee_login'))
    else:
        return render_template('employee/register.html', form=form)


@employees.route('/tickets/<int:s_id>', methods=['GET', 'POST'])
@login_required(role='EMPLOYEE')
def tickets(s_id):
    screening = Screening.query.join(Movie).join(Auditorium) \
        .filter(Screening.id.is_(s_id)) \
        .first_or_404()
    
    seats = Seat.query.filter_by(auditorium_id = screening.auditorium.id).order_by(Seat.id) 

    tickets = Ticket.query.join(Screening).join(Seat) \
        .filter(Screening.id.is_(screening.id)) \
        .order_by(Ticket.id) 
    
    purchase = Purchased_Ticket.query.join(Purchase).join(Ticket).join(Seat) \
        .filter(
            db.and_(
            Purchase.id.is_(Purchased_Ticket.purchase_id),
            Ticket.screening_id.is_(screening.id)))
    
    purchased_tickets = {}
    purchased_seats = {}

    for p in purchase:
        purchased_tickets[p.ticket_id] = p.purchase
        purchased_seats[p.ticket.seat.id] = p.purchase

    total= tickets.count()

    return render_template('employee/tickets.html', title='Tickets', screening=screening, seats=seats, tickets=tickets,\
                            total=total, purchased_tickets=purchased_tickets, purchased_seats=purchased_seats)


# Might not need to use join in some queries (for talbes that reference others)
# For example, in purchase_info, adding a joining with a member table is not needed because purhcase references the member table
# TODO: CHECK ALL PREVIOUS QUERIES some code can be ommited!!!