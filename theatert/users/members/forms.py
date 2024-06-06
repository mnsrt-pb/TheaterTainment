from datetime import datetime
from flask import flash
from flask_wtf import FlaskForm
from flask_login import current_user
from theatert import bcrypt
from theatert.models import Member
from wtforms import BooleanField,  EmailField, HiddenField, PasswordField, StringField, SelectField, SubmitField
from wtforms.validators import DataRequired, EqualTo, Email, Length, ValidationError

import phonenumbers


class AccountInfoForm(FlaskForm):
    def validate_phone(self, phone):
        p = '+1'+ phone.data
        if not phonenumbers.is_valid_number(phonenumbers.parse(p, None)):
            raise ValidationError('Invalid Phone Number.') 
    def validate_dob(self, dob):
        if dob.data != '':
            try:
                datetime.strptime(dob.data, '%m/%d').date()
            except:
                raise ValidationError('The month or day value is not valid for Date of Birth.') 
        
    fname = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    lname = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    dob = StringField('Date of Birth (MM/DD)', validators=[Length(min=0, max=5)])
    phone = StringField('Phone', validators=[DataRequired(),
                                             Length(min=7, max=15, message='The value for the Phone Number field is invalid.')])
    zip_code = StringField('ZIP Code', validators=[DataRequired(),
                                                    Length(min=5, max=5, message='The value for the Billing Zip Code field is invalid.')])
    submit = SubmitField('Save')


# class CheckoutForm(FlaskForm):
#     screening_id = HiddenField(validators=[DataRequired()])
#     seats_selected = HiddenField(validators=[DataRequired()])
#     adult_tickets = HiddenField(validators=[DataRequired()])
#     child_tickets = HiddenField(validators=[DataRequired()])
#     senior_tickets = HiddenField(validators=[DataRequired()])
#     card_type = HiddenField(validators=[DataRequired()])

#     email = EmailField('Email Address', validators=[DataRequired(), Email()])

#     card_number = StringField('Card Number', 
#         validators=[DataRequired(message="The Card Number field is required."), 
#                     Length(min=8, max=19, message='The Card Number field is not a valid credit card number.')])
    
#     exp_month = SelectField(u'Exp Month', coerce=int,
#                             choices=[(1, 'Jan'), 
#                                      (2, 'Feb'), 
#                                      (3, 'Mar'),
#                                      (4, 'Apr'), 
#                                      (5, 'May'),
#                                      (6, 'June'), 
#                                      (7, 'Jul'),
#                                      (8, 'Aug'), 
#                                      (9, 'Sept'),
#                                      (10, 'Oct'),
#                                      (11, 'Nov'), 
#                                      (12, 'Dec')])
    
#     exp_year = SelectField(u'Exp Year', coerce=int,
#                            choices=[(datetime.today().year + x, datetime.today().year + x) for x in range(11)])
    
#     zip_code = StringField('Billing Zip Code', validators=[DataRequired(message="The Billing ZIP Code field is required."),
#                     Length(min=5, max=5, message='The value for the Billing Zip Code field is invalid.')])
    
#     sec_code = StringField('Card Security Code', validators=[DataRequired(message="The Card Security Code field is required."),
#                     Length(min=3, max=4, message='The Card Security Code field is not a valid credit card security code.')])
    
#     submit = SubmitField('Complete Purchase')


class BaseCheckoutForm(FlaskForm):
    screening_id = HiddenField(validators=[DataRequired()])
    seats_selected = HiddenField(validators=[DataRequired()])
    adult_tickets = HiddenField(validators=[DataRequired()])
    child_tickets = HiddenField(validators=[DataRequired()])
    senior_tickets = HiddenField(validators=[DataRequired()])


class BasePaymentForm(FlaskForm):
    def validate_card_type(self, type):
        '''Ensure Select Movie was not selected.'''

        if (type.data != 'Visa') and (type.data != 'American Express') and (type.data != 'Discover') and (type.data != 'Mastercard'):
            flash('Invalid Entry.', 'danger')
            raise ValidationError('Invalid Card Type.')
        
    card_type = HiddenField(validators=[DataRequired()])

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
    

class MemberCheckoutForm(BaseCheckoutForm, BasePaymentForm):
    form1 = HiddenField()
    save = BooleanField('Save my Payment Information')
    submit = SubmitField('Complete Purchase')


class MemberCheckoutForm2(BaseCheckoutForm):
    sec_code = StringField('Card Security Code', validators=[DataRequired(message="The Card Security Code field is required."),
                    Length(min=3, max=4, message='The Card Security Code field is not a valid credit card security code.')])
    submit = SubmitField('Complete Purchase')

 
class CheckoutForm(BaseCheckoutForm, BasePaymentForm):
    email = EmailField('Email Address', validators=[DataRequired(), Email()])
    submit = SubmitField('Complete Purchase')


class DefaultPaymentForm(BasePaymentForm):
    submit = SubmitField('Save')


class DeleteDefaultPayemnt(FlaskForm):
    delete = HiddenField()
    submit = SubmitField('Delete Saved Card')


class EmailForm(FlaskForm):
    def validate_email(self, email):
        '''Ensure email does not exist'''

        email = Member.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('An account with this email already exists.')
    
    def validate_password(self,password):
        if not bcrypt.check_password_hash(current_user.password, password.data):
            raise ValidationError('To change your email address, you must enter the current password for the account.')
        
    email = EmailField('Email Address', validators=[DataRequired(), Email()])
    confirm_email = EmailField('Confirm Email Address', validators=[DataRequired(), Email(), EqualTo('email', message='Emails must match.')])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    submit = SubmitField('Save')


class LoginForm(FlaskForm):
    email = EmailField('Email Address', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Log In')    


class PasswordForm(FlaskForm):
    def validate_current_password(self,current_password):
        if not bcrypt.check_password_hash(current_user.password, current_password.data):
            raise ValidationError('To change your password, you must enter the current password for the account.')
        
    def validate_new_password(self, new_password):
        has_num, has_alpha, has_special_char = False, False, False

        for char in new_password.data:
            if char.isnumeric():
                has_num = True
            elif char.isalpha():
                has_alpha = True
            elif char in '[@_!#$%^&*()<>?/\|}{~:]':
                has_special_char = True

        if not has_num:
            raise ValidationError('Password must have at least one number.')   
        
        if not has_alpha:
            raise ValidationError('Password must have at least one letter.')   
  
        if not has_special_char:
            raise ValidationError('Password must have at least one special character.') 

        
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[DataRequired(), Length(min=8)])
    confirmation = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('new_password', message='The new password and confirmation password do not match.')])
    submit = SubmitField('Save')
 

class RegistrationForm(FlaskForm):
    def validate_email(self, email):
        '''Ensure email does not exist'''

        email = Member.query.filter_by(email=email.data).first()
        if email:
            raise ValidationError('Email already exists.')


    def validate_password(self, password):
        has_num, has_alpha, has_special_char = False, False, False

        for char in password.data:
            if char.isnumeric():
                has_num = True
            elif char.isalpha():
                has_alpha = True
            elif char in '[@_!#$%^&*()<>?/\|}{~:]':
                has_special_char = True

        if not has_num:
            raise ValidationError('Password must have at least one number.')   
        
        if not has_alpha:
            raise ValidationError('Password must have at least one letter.')   
  
        if not has_special_char:
            raise ValidationError('Password must have at least one special character.') 


    def validate_phone(self, phone):
        p = '+1'+ phone.data
        if not phonenumbers.is_valid_number(phonenumbers.parse(p, None)):
            raise ValidationError('Invalid Phone Number.') 


    fname = StringField('First Name', validators=[DataRequired(), Length(min=2, max=50)])
    lname = StringField('Last Name', validators=[DataRequired(), Length(min=2, max=50)])
    email = EmailField('Email Address', validators=[DataRequired(), Email()])
    confirm_email = EmailField('Confirm Email Address', validators=[DataRequired(), Email(), EqualTo('email', message='Emails must match.')])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirmation = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password', message='Passwords must match.')])
    phone = StringField('Phone', validators=[DataRequired(),
                                             Length(min=7, max=15, message='The value for the Phone Number field is invalid.')])
    zip_code = StringField('ZIP Code', validators=[DataRequired(),
                                                    Length(min=5, max=5, message='The value for the Billing Zip Code field is invalid.')])


    agree = BooleanField('I acknowledge that I am at least 16 years of age.', validators=[DataRequired(message='Must be at least 16 years of age.')])

    submit = SubmitField('Register')

