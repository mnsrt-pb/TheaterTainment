from cs50 import SQL
from flask import flash
from flask_wtf import FlaskForm
from theatert.models import Employee, Movie
from wtforms import BooleanField, HiddenField, PasswordField, SelectField,StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError


# Configure CS50 Library to use SQLite database
db = SQL('sqlite:///database/theater.db')


class RegistrationForm(FlaskForm):
    def validate_username(self, username):
        '''Ensure username does not exist'''

        user = Employee.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already exists.')


    def validate_key(self, key):
        if key.data != 'HelloWorld#3': 
            raise ValidationError('Invalid Employee Key.')
        

    def validate_password(self, password):
        has_num, has_upper, has_lower, has_special_char = False, False, False, False

        for char in password.data:
            if char.isnumeric():
                has_num = True
            elif char.isupper():
                has_upper = True
            elif char.islower():
                has_lower = True
            elif char in '[@_!#$%^&*()<>?/\|}{~:]':
                has_special_char = True

        if not(has_num and has_upper and has_lower and has_special_char):
            raise ValidationError('Pasword does not meet requirements.')   


    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirmation = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    key = PasswordField('Employee Key', validators=[DataRequired()])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password',
                             validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')


class SearchMovieForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    release_year = StringField('Release Year', validators=[Length(min=0, max=4)])
    submit = SubmitField('Search')


class AddMovieForm(FlaskForm):
    def validate_m_id(self, m_id):
        '''Ensure movie does not exist'''

        movie = Movie.query.filter_by(tmdb_id=m_id.data).first()
        if movie:
            if movie.deleted == False: # Movie is not flagged "deleted"
                flash('Movie already exists', 'danger')
                raise ValidationError('Movie already exists.')
        
    m_id = HiddenField(validators=[DataRequired()])
    submit = SubmitField('Add Movie')


class InactivateForm(FlaskForm):
    def validate_m_id(self, m_id):
        '''Ensure Select Movie was not selected and movie has been released.'''
        if m_id.data == '-1':
            flash('Must select a movie.', 'danger')
            raise ValidationError('Must select a movie.')
        
    m_id = SelectField('Movie') 
    submit = SubmitField('Inactivate')


class ActivateForm(FlaskForm):
    def validate_m_id(self, m_id):
        '''Ensure Select Movie was not selected and movie has been released.'''
        if m_id.data == '-1':
            flash('Must select a movie.', 'danger')
            raise ValidationError('Must select a movie.')
        
    m_id = SelectField('Movie')
    submit = SubmitField('Activate')


