from flask import flash
from flask_wtf import FlaskForm
from wtforms import HiddenField, SelectField,StringField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError, Optional


class SearchMovieForm(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    release_year = StringField('Release Year', validators=[Length(min=0, max=4)])
    submit = SubmitField('Search')


class AddMovieForm(FlaskForm):        
    m_id = HiddenField(validators=[DataRequired()])
    submit = SubmitField('Add Movie')
    fetch = SubmitField('Fetch New Data')


class InactivateForm(FlaskForm):
    def validate_m_id(self, m_id):
        '''Ensure Select Movie was not selected.'''

        if m_id.data == 'None':
            flash('Must select a movie you wnat to inactivate.', 'danger')
            raise ValidationError('Must select a movie.')
        
    m_id = SelectField('Movie') 
    submit = SubmitField('Inactivate')


class ActivateForm(FlaskForm):
    def validate_m_id(self, m_id):
        '''Ensure Select Movie was not selected.'''

        if m_id.data == 'None':
            flash('Must select a movie you want to activate.', 'danger')
            raise ValidationError('Must select a movie.')
        
    m_id = SelectField('Movie')
    submit = SubmitField('Activate')


class UpdateMovieForm(FlaskForm):
    poster = SelectField('Poster', validators=[Optional()])
    backdrop = SelectField('Backdrop', validators=[Optional()])
    trailer = SelectField('Trailer', validators=[Optional()])
    submit = SubmitField('Update')

