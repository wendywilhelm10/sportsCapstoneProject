from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt

db = SQLAlchemy()
bcrypt = Bcrypt()

def connect_db(app):
    db.app = app
    db.init_app(app)

class User(db.Model):
    """User Model"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.Text, nullable=False, unique=True)
    password = db.Column(db.Text, nullable=False)

    @classmethod
    def signup(cls, username, email, password):
        """Sign up user.  Hashes password and adds user to system.
        """

        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        user = User(username=username, email=email, password=hashed_pwd)

        db.session.add(user)
        return user

    @classmethod
    def register(cls, username, password):
        """Register user w/hashed password & return user."""

        hashed = bcrypt.generate_password_hash(password)
        # turn bytestring into normal (unicode utf) string
        hashed_utf8 = hashed.decode('utf8')

        # return instance of user w/username and hashed password
        return cls(username=username, password=hashed_utf8)

    @classmethod
    def authenticate(cls, username, password):
        """Validate that user exists & password is correct.
           Return user if valid; else return false
        """

        u = User.query.filter_by(username=username).first()

        if u and bcrypt.check_password_hash(u.password, password):
            # return instance of user
            return u
        else:
            return False


class Sport(db.Model):
    """All Sports IDs and Name from API Model"""

    __tablename__ = "sports"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False, unique=True)


class UserSport(db.Model):
    """Sport for User Model"""

    __tablename__ = "user_sports"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    sport_api_id = db.Column(db.Integer, db.ForeignKey('sports.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))


class League(db.Model):
    """League ID and Name from API Model"""

    __tablename__ = "leagues"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)


class UserLeague(db.Model):
    """League for User Model"""

    __tablename__ = "user_leagues"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    league_api_id = db.Column(db.Integer, db.ForeignKey('leagues.id'))
    user_sport_id = db.Column(db.Integer, db.ForeignKey('user_sports.id'))


class Team(db.Model):
    """Team ID and more information from API Model"""

    __tablename__ = "teams"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    stadium_name = db.Column(db.Text)
    stadium_loc = db.Column(db.Text)
    stadium_cap = db.Column(db.Integer)
    website = db.Column(db.Text)
    facebook = db.Column(db.Text)
    twitter = db.Column(db.Text)
    instagram = db.Column(db.Text)
    logo_pic = db.Column(db.Text)


class UserTeam(db.Model):
    """Team for User Model"""

    __tablename__ = "user_teams"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    team_api_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    user_league_id = db.Column(db.Integer, db.ForeignKey('user_leagues.id'))
    notes = db.Column(db.Text)