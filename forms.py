from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, validators, ValidationError
from wtforms.validators import InputRequired, NumberRange

#csrf = CsrfProtect()

class Queryform(FlaskForm):
    searchTerm = StringField(label='searchTerm', validators=[InputRequired('A query is required')])
    maxResults = StringField(label='maxResults', validators=[InputRequired('Please enter a valid number')])
    api_key = StringField('api_key', validators=[InputRequired('Please enter a valid API key')])
    #maxResults = IntegerField('maxResults', validators=[InputRequired('Please enter a valid number'), NumberRange(min=0, max=100, message='Please enter a number from 0 to 100')])
    #submit = SubmitField('Submit')
