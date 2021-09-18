from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, IntegerField, validators, ValidationError


class SignUpForm(FlaskForm):
    searchTerm = StringField(label='', validators=[validators.DataRequired()])
    maxResults = StringField(label='', validators=[validators.DataRequired()])
    submit = SubmitField('Submit')

