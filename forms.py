from flask_wtf import FlaskForm, Form
from wtforms import StringField, PasswordField, SelectField, HiddenField
from wtforms.validators import DataRequired, Email, Length

class UserAddForm(FlaskForm):
    """Form for adding users."""

    username = StringField('Username', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[Length(min=6)])

class UserForm(FlaskForm):
    """Form for logging in users."""

    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[Length(min=6)])

class AddSportForm(FlaskForm):
    """Form for adding a sport for a user."""

    sport = SelectField('Favorite Sport: ', coerce=int)
    sportName = HiddenField('Name')

class AddLeagueForm(Form):
    """Form for adding a league for a user."""

    league = SelectField('Favorite League: ', coerce=int)
    leagueName = HiddenField('Name')

class AddTeamForm(Form):
    """Form for added a team for a user."""

    team = SelectField('Favorite Team: ', coerce=int)