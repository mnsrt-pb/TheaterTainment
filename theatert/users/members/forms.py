from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import HiddenField, EmailField, StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, Length

class CheckoutForm(FlaskForm):
    '''Ensure username does not exist'''
            
    screening_id = HiddenField(validators=[DataRequired()])
    seats_selected = HiddenField(validators=[DataRequired()])
    adult_tickets = HiddenField(validators=[DataRequired()])
    child_tickets = HiddenField(validators=[DataRequired()])
    senior_tickets = HiddenField(validators=[DataRequired()])
    card_type = HiddenField(validators=[DataRequired()])

    email = EmailField('Email Address', validators=[DataRequired(), Email()])
    card_number = StringField('Card Number', 
        validators=[DataRequired(message="The Card Number field is required."), 
                    Length(min=8, max=19, message='The Card Number field is not a valid credit card number.')])
    
    exp_month = SelectField(u'Exp Month', coerce=int,
                            choices=[(1, 'Jan'), 
                                     (2, 'Feb'), 
                                     (3, 'Mar'),
                                     (4, 'Apr'), 
                                     (5, 'May'),
                                     (6, 'June'), 
                                     (7, 'Jul'),
                                     (8, 'Aug'), 
                                     (9, 'Sept'),
                                     (10, 'Oct'),
                                     (11, 'Nov'), 
                                     (12, 'Dec')])
    
    exp_year = SelectField(u'Exp Year', coerce=int,
                           choices=[(datetime.today().year + x, datetime.today().year + x) for x in range(11)])
    
    zip_code = StringField('Billing Zip Code', validators=[DataRequired(message="The Billing ZIP Code field is required."),
                    Length(min=5, max=5, message='The value for the Billing Zip Code field is invalid.')])
                                                           
    sec_code = StringField('Card Security Code', validators=[DataRequired(message="The Card Security Code field is required."),
                    Length(min=3, max=4, message='The Card Security Code field is not a valid credit card security code.')])
    
    submit = SubmitField('Complete Purchase')
