from flask_wtf import FlaskForm, CsrfProtect
from wtforms import StringField, PasswordField, SubmitField, IntegerField, validators, ValidationError
from wtforms.validators import InputRequired, NumberRange

csrf = CsrfProtect()

class Queryform(FlaskForm):
    print("Inside query form")
    searchTerm = StringField(label='searchTerm', validators=[InputRequired('A query is required')])
    maxResults = StringField(label='maxResults', validators=[InputRequired('Please enter a valid number')])
    #maxResults = IntegerField('maxResults', validators=[InputRequired('Please enter a valid number'), NumberRange(min=0, max=100, message='Please enter a number from 0 to 100')])
    #submit = SubmitField('Submit')
    print(f'SearchTerm:{searchTerm}, max_results: {maxResults}')
