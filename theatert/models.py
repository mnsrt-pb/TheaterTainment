from datetime import datetime 
from theatert import db, login_manager
from flask_login import UserMixin


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
    email = db.Column(db.String(120), unique = True, nullable=False)
    f_name = db.Column(db.String(20), nullable=False)
    l_name = db.Column(db.String(20), nullable=False)

    __mapper_args__ = {
        'polymorphic_identity': 'MEMBER',
    }


    def __repr__(self):
        return f"User({self.id}, {self.role}, {self.username}, {self.email}, {self.f_name}, {self.l_name})"


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
                             backref=db.backref('movies', lazy=True))
    
    def __repr__(self):
        return f"Movie({self.id}, {self.tmdb_id}, {self.title}, {self.status}, {self.overview}, {self.release_date}, {self.runtime}, {self.tagline}, {self.active}, {self.deleted}, {self.genres})"


class Genre(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), nullable=False)
    
    def __repr__(self):
        return f"Genre({self.id}, {self.name})"
