from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class SignInForm(FlaskForm):
    submit = SubmitField('Sign in to Spotify!')
