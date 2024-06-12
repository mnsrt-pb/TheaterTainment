from datetime import datetime, timedelta
from flask import Blueprint, flash, render_template,  redirect, request, url_for
from flask_login import current_user
from sqlalchemy import collate
from theatert import db
from theatert.users.employees.showtimes.forms import AddShowtime
from theatert.models import Auditorium, Change, Movie, Screening, Seat, Ticket
from theatert.users.utils import date_obj, login_required
from theatert.users.employees.showtimes.utils import get_showtimes


showtimes = Blueprint('showtimes', __name__, url_prefix='/showtimes')


@showtimes.route('/add-showtime', methods=['GET', 'POST'])
@login_required(role="EMPLOYEE")
def add_showtime():
    ''' Add showtime for selected movie '''

    form = AddShowtime()

    movies = Movie.query.filter(
                        db.and_(
                            Movie.deleted.is_(False), 
                            Movie.active.is_(True),
                            db.ColumnOperators.__le__(Movie.release_date, (datetime.now() + timedelta(days=20)))
                        )).order_by(collate(Movie.title, 'NOCASE'))
    
    choices = [(None, 'Select Movie')]
    for m in movies:
        choices.append((m.id, m.title))
    form.m_id.choices=choices

    auditoriums = Auditorium.query.all()
    choices = [(None, 'Select Auditorium')]
    for a in auditoriums:
        choices.append((a.id, a.id))
    form.a_id.choices = choices

    if request.method == 'GET':
        form.adult_price.data = 12.50
        form.child_price.data = 10.50
        form.senior_price.data = 9.00

        form.date_time.data = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
    else:
        if form.validate_on_submit():
            movie = Movie.query.get(form.m_id.data)
            end_dt = form.date_time.data + timedelta(minutes=(movie.runtime)+20) # 20 min for advertisements

            # Ensure a movie isn't screening at auditorium during the entered time.
            exists = Screening.query.filter(
                db.or_(
                    db.and_(
                        Screening.auditorium_id.is_(form.a_id.data), 
                        db.ColumnOperators.__ge__(Screening.end_datetime, end_dt),
                        db.ColumnOperators.__le__(Screening.start_datetime, end_dt),
                    ),
                    db.and_(
                        Screening.auditorium_id.is_(form.a_id.data), 
                        db.ColumnOperators.__ge__(Screening.end_datetime, form.date_time.data),
                        db.ColumnOperators.__le__(Screening.start_datetime, form.date_time.data),
                    )
                )).first()
            
            if exists:
                flash(f'A movie will screen at Auditorium {form.a_id.data} at this time. Try a different auditorium or time.', 'danger')
            elif form.date_time.data < movie.release_date:
                # Ensure movie's date and time are after movie's release date
                flash(f'{movie.title} has not been released for the date entered.', 'danger')
            else: 
                # Add screening
                screening = Screening(
                    start_datetime = form.date_time.data,
                    end_datetime = end_dt,
                    adult_price = form.adult_price.data,
                    child_price = form.child_price.data,
                    senior_price = form.senior_price.data,
                    auditorium_id = form.a_id.data,
                    movie_id = form.m_id.data
                )
                db.session.add(screening)
                db.session.commit()

                # Add employee change
                change = Change(
                    action = "added",
                    table_name = "screening",
                    data_id = screening.id,
                    employee_id = current_user.id
                )
                db.session.add(change)

                # Generate tickets
                seats=Seat.query.filter_by(auditorium_id = form.a_id.data).order_by(Seat.id)

                for s in seats:
                    if s.seat_type != 'empty':
                        ticket = Ticket(
                            screening_id = screening.id,
                            seat_id = s.id
                        )
                        db.session.add(ticket)

                flash('Showtime was created and tickets have been generated.', 'light')

                db.session.commit()
            
                return redirect(url_for('employees.showtimes.movie', movie_route=movie.route))

    return render_template('employee/add-showtime.html', form=form)


@showtimes.route('/all-showtimes', methods=['GET', 'POST'])
@login_required(role="EMPLOYEE")
def all_showtimes():
    ''' Display all showtimes '''
    
    auditorium = request.args.get('auditorium', None, type=int)
    date = request.args.get('date', None, type=date_obj)
    page = request.args.get('page', 1, type=int)
    
    screenings, choices, total, movies, seats_total = get_showtimes(auditorium, date, page, '', None)
 
    return render_template('employee/showtimes.html', title='All Showtimes', \
                            screenings=screenings, movies=movies, \
                            seats_total=seats_total, total=total, url='employees.showtimes.all_showtimes', \
                            choices=choices, auditorium=auditorium, date=date)
                         

@showtimes.route('/<string:movie_route>')
@login_required(role="EMPLOYEE")
def movie(movie_route):
    ''' Display movie's showtimes '''

    screenings, choices, total, movie, seats_total =  get_showtimes(
        request.args.get('auditorium', None, type=int), 
        request.args.get('date', None, type=date_obj), 
        request.args.get('page', 1, type=int),   
        '', movie_route
    )

    form = AddShowtime()
    form.m_id.choices = [(movie.id, movie.title)]
    form.a_id.choices = choices
    form.adult_price.data = 12.50
    form.child_price.data = 10.50
    form.senior_price.data = 9.00

    form.date_time.data = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)

    return render_template('employee/showtimes-movie.html', title=movie.title, screenings=screenings, \
                           seats_total=seats_total, total=total, url='employees.showtimes.movie', \
                            movie_route=movie_route, choices=choices, form=form)


@showtimes.route('/past-showtimes')
@login_required(role="EMPLOYEE")
def past_showtimes():
    ''' Display past showtimes '''

    screenings, choices, total, movies, seats_total = get_showtimes(
        request.args.get('auditorium', None, type=int), 
        request.args.get('date', None, type=date_obj), 
        request.args.get('page', 1, type=int), 
        'past', None
    )
    
    return render_template('employee/showtimes.html', title='Past Showtimes', \
                           screenings=screenings, movies=movies, \
                           seats_total=seats_total, total=total,  url='employees.showtimes.past_showtimes', \
                            choices=choices)
  

@showtimes.route('/upcoming-showtimes')
@login_required(role="EMPLOYEE")
def upcoming_showtimes():
    '''  Display upcoming showtimes '''

    screenings, choices, total, movies, seats_total = get_showtimes(
        request.args.get('auditorium', None, type=int), 
        request.args.get('date', None, type=date_obj), 
        request.args.get('page', 1, type=int), 
        'upcoming', None
    )
    
    return render_template('employee/showtimes.html', title='Upcoming Showtimes', \
                            screenings=screenings, movies=movies, \
                            seats_total=seats_total, total=total,  url='employees.showtimes.upcoming_showtimes', \
                            choices=choices)

