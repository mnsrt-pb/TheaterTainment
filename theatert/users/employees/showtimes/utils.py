from datetime import datetime
from sqlalchemy import extract
from theatert import db
from theatert.models import Auditorium, Movie, Screening, Seat


def get_showtimes(get_auditorium, get_date, get_page, adjust, movie_route):
    ''' Return showtimes and their info according to filters.'''

    # Auditoriums needed for filter
    auditoriums = Auditorium.query.all()
    choices = [(None, 'Select Auditorium')]
    for a in auditoriums:
        choices.append((a.id, a.id))
    
    if movie_route:
        movie = Movie.query.filter_by(route = movie_route, deleted=False).first_or_404()
        screenings = Screening.query.filter(Screening.movie_id.is_(movie.id))

    else:
        screenings = Screening.query

    screenings = screenings.filter(
            db.and_(
                extract('year', Screening.start_datetime).is_(get_date.year),
                extract('month', Screening.start_datetime).is_(get_date.month),
                extract('day', Screening.start_datetime).is_(get_date.day)
        )) if get_date else screenings

    screenings = screenings.filter(Screening.auditorium_id.is_(get_auditorium)) if get_auditorium else screenings

    screenings = screenings.order_by(Screening.start_datetime.desc())

    if adjust == 'upcoming':
        screenings = screenings.filter(db.ColumnOperators.__ge__(Screening.end_datetime, datetime.now())) \
        .order_by(Screening.start_datetime.desc()) 
    elif adjust == 'past':
        screenings = screenings.filter(db.ColumnOperators.__lt__(Screening.end_datetime, datetime.now())) \
        .order_by(Screening.start_datetime.desc())

    total = screenings.count()

    if movie_route:
        data = movie
    else:
        data = screenings.group_by(Screening.movie_id)

    screenings = screenings.paginate(page=get_page, per_page=10)

    seats_total = []
    for s in screenings:
        seats_total.append(Seat.query.filter(
                    db.and_(
                        Seat.auditorium_id.is_(s.auditorium.id), 
                        Seat.seat_type.is_not('empty'))).count())


    return screenings, choices, total, data, seats_total
