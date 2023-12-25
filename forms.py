from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import ValidationError, InputRequired, DataRequired, Length, Email, EqualTo


class RegistrationForm(FlaskForm):
    def validate_key(form, key):
        if key.data != 'ASDF123!!45': 
            raise ValidationError('Invalid Employee Key.')
        
    def validate_password(form, password):
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

    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password',
                             validators=[DataRequired(), Length(min=8)])
    confirmation = PasswordField('Confirm Password',
                             validators=[DataRequired(), EqualTo('password', message='Passwords must match')])
    e_key = PasswordField('Employee Key',
                             validators=[DataRequired(), validate_key])
    submit = SubmitField('Register')


class LoginForm(FlaskForm):
    username = StringField('Username', 
                           validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password',
                             validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')

