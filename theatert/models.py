from datetime import datetime 
from theatert import db, login_manager
from flask_login import UserMixin
from secrets import token_urlsafe


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Users
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique = True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'ANY',
        'polymorphic_on': role
    }


    def __repr__(self):
        return f"User({self.id}, {self.role}, {self.username})"
    

class Employee(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    changes = db.relationship('Change', backref='author', lazy=True)

    __mapper_args__ = {
        'polymorphic_identity': 'EMPLOYEE',
    }


class Member(User):
    id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    email = db.Column(db.String, unique = True, nullable=False)
    fname = db.Column(db.String, nullable=False)
    lname = db.Column(db.String, nullable=False)
    phone = db.Column(db.Integer, nullable=False)
    zip_code = db.Column(db.Integer, nullable=False)
    dob = db.Column(db.Date)

    cards = db.relationship('Cards', backref='member', lazy=True) # Can have many cards
    watchlist = db.relationship('Watchlist', backref='member', lazy=True) # Can have many movies
    purchase_id = db.relationship('Purchase', backref='member', lazy=True) # Can be a part of many purchases

    __mapper_args__ = {
        'polymorphic_identity': 'MEMBER',
    }


    def __repr__(self):
        return f"User({self.id}, {self.role}, {self.username}, {self.email}, {self.fname}, {self.lname})"


class Change(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(10), nullable=False)
    table_name = db.Column(db.String(10), nullable=False)
    data_id = db.Column(db.Integer, nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    employee_id = db.Column(db.Integer, db.ForeignKey('employee.id'), nullable=False)


    def __repr__(self):
        return f"Change({self.id}, {self.action}, {self.table_name}, {self.data_id}, {self.date})"


# Movies
genres = db.Table('genres',
    db.Column('movie_id', db.Integer, db.ForeignKey('movie.id'), primary_key=True),
    db.Column('genre_id', db.Integer, db.ForeignKey('genre.id'), primary_key=True)
)


class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tmdb_id = db.Column(db.Integer, unique=True, nullable=False)
    title = db.Column(db.String, nullable=False)
    route = db.Column(db.String, unique=True, nullable=False)
    status = db.Column(db.String)
    overview = db.Column(db.String)
    release_date = db.Column(db.DateTime)
    runtime = db.Column(db.Integer)
    tagline = db.Column(db.String)
    rating = db.Column(db.String)
    poster_path = db.Column(db.String)
    backdrop_path = db.Column(db.String)
    trailer_path = db.Column(db.String)
    active = db.Column(db.Boolean, default=False, nullable=False)
    deleted = db.Column(db.Boolean, default=False, nullable=False)

    genres = db.relationship('Genre', secondary=genres, lazy='subquery', 
                             backref=db.backref('movies', lazy=True)) # Can have many genres
    screenings = db.relationship('Screening', backref='movie', lazy=True) # Can have many screenings
    watchlist = db.relationship('Watchlist', backref='movie', lazy=True) # Can be a part of many watchlists
    
    def __repr__(self):
        return f"Movie({self.id}, {self.tmdb_id}, {self.title}, Active:{self.active}, Deleted:{self.deleted}, Poster:{self.poster_path}, Backdrop:{self.backdrop_path}, Trailer:{self.trailer_path}, {self.status}, {self.overview}, {self.release_date}, {self.runtime}, {self.tagline}, {self.genres})"


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    
    def __repr__(self):
        return f"Genre({self.id}, {self.name})"


class Watchlist(db.Model):
    id = db.Column(db.Integer, primary_key=True) 

    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False) # Has one member
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False) # Has one movie

    def __repr__(self): 
        return f"Id:({self.id}, Member: {self.member_id}, Movie: {self.movie_id})"


# Auditoriums & Seats
class Auditorium(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rows = db.Column(db.Integer, nullable=False)
    cols = db.Column(db.Integer, nullable=False)

    seats = db.relationship('Seat', backref='auditorium', lazy=True) # Can have many seats
    screenings = db.relationship('Screening', backref='auditorium', lazy=True) # Can have many screenings

    def __repr__(self):
        return f"Auditorium({self.id}, {self.rows}, {self.cols})"


class Seat(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    row = db.Column(db.Integer, nullable=False)
    col = db.Column(db.Integer, nullable=False)
    row_name = db.Column(db.String, nullable=False)
    seat_type = db.Column(db.String)

    auditorium_id = db.Column(db.Integer, db.ForeignKey('auditorium.id'), nullable=False) # Has one auditorium
    tickets = db.relationship('Ticket', backref='seat', lazy=True) # Can be assigned to many tickets

    def __repr__(self):
        return f"Seat({self.id}, {self.row}, {self.row_name}, {self.col}, {self.seat_type}, Auditorium: {self.auditorium_id})"


# Screenings & Tickets
class Screening(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    start_datetime = db.Column(db.DateTime, nullable=False)
    end_datetime = db.Column(db.DateTime, nullable=False)
    adult_price = db.Column(db.Numeric, nullable=False)
    child_price = db.Column(db.Numeric, nullable=False)
    senior_price = db.Column(db.Numeric, nullable=False)

    auditorium_id = db.Column(db.Integer, db.ForeignKey('auditorium.id'), nullable=False) # Has one auditorium
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), nullable=False) # Has one movie

    tickets = db.relationship('Ticket', backref='screening', lazy=True) # Can have many tickets

    def __repr__(self):
        return f"Screening({self.id}, {self.start_datetime}, {self.end_datetime}, {self.adult_price}, {self.child_price}, {self.senior_price}, Auditorium: {self.auditorium_id}, Movie: {self.movie_id})"


class Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True) 

    screening_id = db.Column(db.Integer, db.ForeignKey('screening.id'), nullable=False) # Has one screening
    seat_id = db.Column(db.Integer, db.ForeignKey('seat.id'), nullable=False) # Has one seat

    purchased = db.relationship('Purchased_Ticket', backref='ticket', lazy=True) # Can have many tickets

    def __repr__(self): 
        return f"Ticket({self.id}, Screening: {self.screening_id}, Seat: {self.seat_id})"


# Purchasing Tickets
class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    member = db.Column(db.Boolean, default=True, nullable=False) 
    # An instance of this card should at most appear twice
    # Once for members and once for guests

    card_num = db.Column(db.Integer, nullable=False) 
    sec_code = db.Column(db.Integer, nullable=False)
    exp_date = db.Column(db.Date, nullable=False)
    card_type = db.Column(db.String(10), nullable=False)
    billing_zip = db.Column(db.Integer, nullable=False) 

    cards_id = db.relationship('Cards', backref='card', lazy=True) # Can be a part of many card groups
    purchase_id = db.relationship('Purchase', backref='card', lazy=True) # Can be a part of many card groups

    def __repr__(self): 
        return f"Card({self.id}, Num:{self.card_num}, Sec:{self.sec_code}, Exp:{self.exp_date}, Zip:{self.billing_zip}, Type:{self.card_type}, Member:{self.member})"


class Cards(db.Model): 
    id = db.Column(db.Integer, primary_key=True) 
    active = db.Column(db.Boolean, default=True, nullable=False)

    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False) # Has one member
    card_id = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=False) # Has one card

    def __repr__(self): 
        return f"Cards({self.id}, Active:{self.active}, Member: {self.member_id}, Card: {self.card_id})"


class Purchase(db.Model):
    id = db.Column(db.Integer, primary_key=True) 
    confirmation = db.Column(db.String, unique = True)

    email = db.Column(db.String, nullable=False)
    datetime = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    adult_tickets = db.Column(db.Integer, nullable=False)
    child_tickets = db.Column(db.Integer, nullable=False)
    senior_tickets = db.Column(db.Integer, nullable=False)

    card_id = db.Column(db.Integer, db.ForeignKey('card.id'), nullable=False) # Has one card
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=True) # Can have a member
    purchased_ticket_id = db.relationship('Purchased_Ticket', backref='purchase', lazy=True) # Can have many purchased tickets

    def __repr__(self): 
        return f"Purchase({self.id}, confirmation:{self.confirmation}, {self.email}, {self.datetime}, adult: {self.adult_tickets}, child: {self.child_tickets}, senior: {self.senior_tickets}, Card: {self.card_id}))"


class Purchased_Ticket(db.Model):
    id = db.Column(db.Integer, primary_key=True) 

    ticket_id = db.Column(db.Integer, db.ForeignKey('ticket.id'), nullable=False) # Has one ticket
    purchase_id = db.Column(db.Integer, db.ForeignKey('purchase.id'), nullable=False) # Has one purchase group

    def __repr__(self): 
        return f"Purchased Ticket({self.id}, Ticket: {self.ticket_id}, Purchase Group: {self.purchase_id})"

