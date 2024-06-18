from datetime import datetime
from flask_wtf import FlaskForm
from theatert import min_price, max_price, start_time, end_time
from wtforms import DecimalField, SelectField, SubmitField
from wtforms.fields import DateTimeLocalField
from wtforms.validators import DataRequired, ValidationError

def places():
    message = f'Must have at most two values after the decimal.'

    def _places(form, field):
        try:
            if len(str(field.data).split(".")[1]) > 2:
                raise ValidationError(message)
        except:
            pass
    
    return _places

def price():
    message = f'Must be between ${min_price} and ${max_price}.'

    def _price(form, field):
        if field.data < min_price or field.data > max_price:
            raise ValidationError(message)
    
    return _price

class AddShowtime(FlaskForm):
    def validate_m_id(self, m_id):
        '''Ensure Select Movie was not selected and movie has been released.'''

        if m_id.data == 'None':
            raise ValidationError('Must select a movie.')
    
    def validate_a_id(self, a_id):
        '''Ensure Select Auditorium was not selected '''

        if a_id.data == 'None':
            raise ValidationError('Must select an auditorium.')
    
    def validate_date_time(self, date_time):
        '''Ensure the date has not passed and time is within screening hours.'''
        if date_time.data < datetime.now():
            raise ValidationError('This date/time has passed!')
        elif date_time.data < datetime(date_time.data.year, date_time.data.month, date_time.data.day, start_time, 00):
            raise ValidationError('Invalid time.')
        elif date_time.data > datetime(date_time.data.year, date_time.data.month, date_time.data.day, end_time, 00):
            raise ValidationError('Invalid time.')

        
    m_id = SelectField('Movie', validators=[DataRequired()]) 
    a_id = SelectField('Auditorium', validators=[DataRequired()]) 

    date_time = DateTimeLocalField('Date and Time ', validators=[DataRequired()])

    adult_price = DecimalField('Adult Price', places=2, validators=[DataRequired(), price(), places()])
    child_price = DecimalField('Child Price', places=2, validators=[DataRequired(), price(), places()])
    senior_price = DecimalField('Senior Price', places=2, validators=[DataRequired(), price(), places()])
    submit = SubmitField('Add Showtime')
