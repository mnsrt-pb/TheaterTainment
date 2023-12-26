from datetime import datetime 
from theatert import db, login_manager
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


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

