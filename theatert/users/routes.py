from datetime import datetime, timedelta
from flask import abort, Blueprint, flash, render_template,  redirect, request, session, url_for
from flask_login import current_user, login_user, logout_user
from pytz import timezone, utc
from secrets import token_urlsafe
from sqlalchemy import extract, collate
from theatert import bcrypt, db
from theatert.models import Employee, Member, Movie, Screening, Seat, Ticket, Card, Purchase, Purchased_Ticket, Watchlist
from theatert.users.members.forms import CheckoutForm
from theatert.users.employees.forms import LoginForm as EmployeeLoginForm
from theatert.users.members.forms import LoginForm as MemberLoginForm, MemberCheckoutForm
from theatert.users.utils import apology, date_obj, guest_or_member, populate_db
from werkzeug.datastructures import MultiDict

import calendar


users = Blueprint('users', __name__)

tz = timezone('US/Eastern')


@users.route('/checkout', methods=['GET', 'POST'])
@guest_or_member()
def checkout():
    ''' Checkout page '''

    form = CheckoutForm()
    member_form = MemberCheckoutForm()

    form_data = session.get('form_data')
    
    if form_data:
        form = CheckoutForm(MultiDict(form_data))
        screening = Screening.query \
            .filter(Screening.id.is_(form.screening_id.data)) \
            .first_or_404()
        
        if screening.start_datetime < datetime.now():
            abort(404)
        
        seats = [ Seat.query.filter_by(auditorium_id = screening.auditorium.id, id = x).first()
            for x in form.seats_selected.data.split(',') ]
        
        tickets = { 'adult': int(form.adult_tickets.data), 
            'child': int(form.child_tickets.data), 
            'senior': int(form.senior_tickets.data) }
        
        show_form = True
        
        form.validate()
    
    else:
        screening = Screening.query \
            .filter(Screening.id.is_(request.form.get('screening_id'))) \
            .first_or_404()
        
        if screening.start_datetime < datetime.now():
            abort(404)

        seats = [ Seat.query.filter_by(auditorium_id = screening.auditorium.id, id = x).first()
            for x in request.form.get('seats_selected').split(',') ]

        tickets = { 'adult': int(request.form.get('adult_tickets')), 
                    'child': int(request.form.get('child_tickets')), 
                    'senior': int(request.form.get('senior_tickets')) }

        form.screening_id.data = screening.id
        form.seats_selected.data = request.form.get('seats_selected')
        form.adult_tickets.data = request.form.get('adult_tickets')
        form.child_tickets.data = request.form.get('child_tickets')
        form.senior_tickets.data = request.form.get('senior_tickets')
        form.screening_id.data = screening.id

        member_form.screening_id.data = screening.id
        member_form.seats_selected.data = request.form.get('seats_selected')
        member_form.adult_tickets.data = request.form.get('adult_tickets')
        member_form.child_tickets.data = request.form.get('child_tickets')
        member_form.senior_tickets.data = request.form.get('senior_tickets')
        show_form = False

    return render_template('guest/checkout.html', screening=screening, seats=seats, tickets=tickets, form=form, show_form=show_form, member_form=member_form)


@users.route('/checkout-validate', methods=['POST'])
@guest_or_member()
def checkout_validate():
    '''  Validate checkout data  '''

    form = CheckoutForm()

    if form.validate_on_submit():
        screening = Screening.query \
            .filter(Screening.id.is_(form.screening_id.data)) \
            .first_or_404()
        
        if screening.start_datetime < datetime.now():
            abort(404)

        form_data = session.get('form_data') 
        if form_data: 
            # saved data form previous submittd form because current submission failed 
            # (screening_id, adult_tickets, etc.)
            session.pop('form_data')

        day = str(calendar.monthrange(form.exp_year.data, form.exp_month.data)[1])
        exp_date = datetime.strptime(str(form.exp_month.data) + '/' + day + '/' + str(form.exp_year.data), '%m/%d/%Y').date()

        card = Card.query.filter_by(card_num = form.card_number.data, member = False).first()

        if card:
            if not (bcrypt.check_password_hash(card.sec_code, form.sec_code.data) \
                and card.exp_date == exp_date and card.card_type == form.card_type.data \
                and card.billing_zip == int(form.zip_code.data)): # Data does not match
            
                flash('Invalid card.', 'danger')
                session['form_data'] = request.form
                return redirect(url_for('users.checkout'))

        else:
            card = Card.query.filter_by(card_num = form.card_number.data, member = True).first()
            
            # Cards with the same card number's must have the same data (sec_code, exp_date, and billing_zip)
            # A card can be saved in the Card table at most twice (once for member's and once for guests)
            if card:
                if not (bcrypt.check_password_hash(card.sec_code, form.sec_code.data) \
                    and card.exp_date == exp_date and card.card_type == form.card_type.data \
                    and card.billing_zip == int(form.zip_code.data)):

                    flash('Invalid card.', 'danger')
                    session['form_data'] = request.form
                    return redirect(url_for('users.checkout'))
            
            card = Card(
                card_num = form.card_number.data,
                sec_code = bcrypt.generate_password_hash(form.sec_code.data).decode('utf-8'),
                exp_date = exp_date,
                card_type = form.card_type.data,
                billing_zip = form.zip_code.data,
                member = False
            )
            db.session.add(card)
            db.session.commit()

        purchase = Purchase(
            email = form.email.data,
            adult_tickets = form.adult_tickets.data,
            child_tickets = form.child_tickets.data,
            senior_tickets = form.senior_tickets.data,
            card_id = card.id,
            confirmation = token_urlsafe(12)
        )
        db.session.add(purchase)

        seat_ids = list(form.seats_selected.data.split(","))
        tickets = ''

        for s in seat_ids:
            ticket = Ticket.query \
                .filter(
                    db.and_(Ticket.seat_id.is_(s),
                            Ticket.screening_id.is_(form.screening_id.data))).first()
            
            tickets += ticket.seat.row_name + str(ticket.seat.col) + ' '
            
            purchased_ticket = Purchased_Ticket.query.filter_by(ticket_id = ticket.id).first()
            
            if purchased_ticket:
                flash(ticket.seat.row_name + str(ticket.seat.col) + ' is unavailable.', 'danger')
                return redirect(url_for('users.ticket_seat_map', showtime_id = form.screening_id.data))
            else:
                purchased_ticket = Purchased_Ticket(
                    ticket_id = ticket.id,
                    purchase_id = purchase.id
                )
                db.session.add(purchased_ticket)

        # Everything's ok, commit changes
        db.session.commit()
        return redirect(url_for('users.receipt', confirmation=purchase.confirmation))
    else:
        session['form_data'] = request.form
        return redirect(url_for('users.checkout'))


@users.route('/employee/login', methods=['GET', 'POST'])
def employee_login():
    ''' Login employee '''

    if current_user.is_authenticated:
        if current_user.role == 'EMPLOYEE':
            return redirect(url_for('employees.home'))
        else:
            return redirect(url_for('users.home'))

    form = EmployeeLoginForm()
    if form.validate_on_submit():
        user = Employee.query.filter_by(username=form.username.data).first()

        # Ensure username exists and password is correct
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')

            return redirect(next_page) if next_page else redirect(url_for('employees.home'))
        
        flash('Invalid Username or Password.', 'danger')

    return render_template('/employee/login.html', form=form)


@users.route('/member/login', methods=['GET', 'POST'])
def member_login():
    ''' Login member '''

    if current_user.is_authenticated:
        if current_user.role == 'EMPLOYEE':
            return redirect(url_for('employees.home'))
        else:
            return redirect(url_for('users.home'))

    form = MemberLoginForm()
    if form.validate_on_submit():
        user = Member.query.filter_by(email=form.email.data).first()

        # Ensure username exists and password is correct
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')

            return redirect(next_page) if next_page else redirect(url_for('users.home'))
        
        flash('Invalid Email or Password.', 'danger')

    return render_template('/member/login.html', form=form)


@users.route('/', methods=['GET', 'POST'])
@guest_or_member()
def home():
    ''' Home page '''

    date = request.args.get('date', default=datetime.today(), type=date_obj)
    max_days = 41
    date = date if (date <= (datetime.today() + timedelta(days=max_days))) and (date >= datetime.today()) else datetime.today()

    movies = Movie.query.filter_by(deleted=False, active=True).order_by(collate(Movie.title, 'NOCASE'))
    dates =[datetime.today() + timedelta(days=x) for x in range(max_days)]

    # movies with showtimes for given date
    m_showtimes = Screening.query.join(Movie) \
        .filter(
            db.and_(
                extract('year', Screening.start_datetime).is_(date.year),
                extract('month', Screening.start_datetime).is_(date.month),
                extract('day', Screening.start_datetime).is_(date.day),
            )).group_by(Screening.movie_id).order_by(collate(Movie.title, 'NOCASE'))
    
    # showtimes for each movie
    s_showtimes = []
    for s in m_showtimes:
        st = Screening.query \
        .filter(
            db.and_(
                Screening.movie_id.is_(s.movie_id),
                extract('year', Screening.start_datetime).is_(date.year),
                extract('month', Screening.start_datetime).is_(date.month),
                extract('day', Screening.start_datetime).is_(date.day),
            )).order_by(Screening.start_datetime)
        s_showtimes.append(st)
    

    watchlist = Watchlist.query.filter(Watchlist.member_id.is_(current_user.id)) if current_user.is_authenticated else None

    return render_template('guest/home.html', movies=movies, dates=dates, m_showtimes=m_showtimes, s_showtimes=s_showtimes, timenow=datetime.now(tz), date=date, watchlist=watchlist)


@users.route('/movie/<string:movie_route>')
@guest_or_member()
def movie(movie_route):
    ''' 
        Display movie details along with a poster, backdrop, and trailer.
        Display upcoming showtimes.
     
    '''

    date = request.args.get('date', default=datetime.today(), type=date_obj)
    max_days = 12
    date = date if (date <= (datetime.today() + timedelta(days=max_days))) and (date >= datetime.today()) else datetime.today()

    movie = Movie.query.filter_by(route = movie_route, deleted=False, active=True).first_or_404()
    dates =[datetime.now(tz) + timedelta(days=x) for x in range(max_days)]

    showtimes = Screening.query \
    .filter(
        db.and_(
            Screening.movie_id.is_(movie.id),
            extract('year', Screening.start_datetime).is_(date.year),
            extract('month', Screening.start_datetime).is_(date.month),
            extract('day', Screening.start_datetime).is_(date.day),
        )).order_by(Screening.start_datetime)

    watchlist = Watchlist.query.filter(Watchlist.member_id.is_(current_user.id)) if current_user.is_authenticated else None

    return render_template('member/movie.html', ext="member/layout.html", Movie=movie, dates=dates, showtimes=showtimes, date=date, timenow=datetime.now(tz), watchlist=watchlist)


@users.route('/movies')
@guest_or_member()
def movies():
    ''' Display all movies '''

    movies = Movie.query.filter(
                db.and_(Movie.deleted.is_(False), Movie.active.is_(True), \
                db.ColumnOperators.__le__(Movie.release_date, datetime.now(tz))))\
                .order_by(collate(Movie.title, 'NOCASE'))

    watchlist = Watchlist.query.filter(Watchlist.member_id.is_(current_user.id)) if current_user.is_authenticated else None

    return render_template('member/movies.html', type='Now Playing', first='type-selected', movies=movies, watchlist=watchlist)


@users.route('/movies/coming-soon')
@guest_or_member()
def movies_coming_soon():
    ''' Display movies that are coming soon '''

    movies = Movie.query.filter(db.and_(Movie.deleted.is_(False), Movie.active.is_(True), \
                db.ColumnOperators.__ge__(Movie.release_date, datetime.now(tz))))\
                .order_by(collate(Movie.title, 'NOCASE'))
    
    watchlist = Watchlist.query.filter(Watchlist.member_id.is_(current_user.id)) if current_user.is_authenticated else None

    return render_template('member/movies.html', type='Coming Soon', second='type-selected', movies=movies, watchlist=watchlist)


@users.route('/logout')
def logout():
    '''Log user out'''

    logout_user()

    # Redirect user to login form 
    return redirect(url_for('users.home'))


@users.route('/receipt/<string:confirmation>')
@guest_or_member()
def receipt(confirmation):
    ''' Display receipt with purchase, showtime, and transaction info. '''

    tickets = Purchased_Ticket.query.join(Purchase) \
        .filter(Purchase.confirmation.is_(confirmation))
    
    purchase = tickets.first_or_404().purchase

    screening = Screening.query \
        .filter(Screening.id.is_(tickets.first().ticket.screening_id)).first()


    return render_template('/guest/receipt.html', purchase=purchase, tickets=tickets, screening=screening, total=tickets.count(), utc=utc, tz=tz)


@users.route('/ticket-seat-map/<int:showtime_id>')
@guest_or_member()
def ticket_seat_map(showtime_id):
    '''  
        Display map for showtime. 
        Allow users to select seats they wish to purchase and ticket types.
        They can proceed to checkout after making their selection.
    
        Note: 
            Cannot purchase a ticket for a movie that's already playing or has played
            Links to these showtimes become unavailable if the movie has played or is currently playing
    '''

    form_data = session.get('form_data')
    form2_data = session.get('form2_data')
    form_data_login = session.get('form_data_login')
    
    if form_data:
        session.pop('form_data')
    if form2_data:
        session.pop('form2_data')
    if form_data_login:
        session.pop('form_data_login')

    screening = Screening.query \
        .filter(Screening.id.is_(showtime_id)) \
        .first_or_404()
    
    if screening.start_datetime < datetime.now():
        abort(404)
    
    seats = Seat.query.filter_by(auditorium_id = screening.auditorium.id).order_by(Seat.id) 

    purchased_ticket = Ticket.query.join(Purchased_Ticket) \
        .filter(
            db.and_(
                Ticket.screening_id.is_(screening.id),
                Purchased_Ticket.ticket_id.is_(Ticket.id)))
    
    purchased_seats = []
    for t in purchased_ticket:
        purchased_seats.append(t.seat.id)

    return render_template('/guest/map.html', screening=screening, seats=seats, purchased_seats=purchased_seats)


@users.route('/todo', methods=['GET', 'POST'])
def todo():
    return apology('TODO', 'member/layout.html', 403)

