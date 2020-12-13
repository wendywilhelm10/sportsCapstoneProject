"""View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_views.py

from unittest import TestCase
from models import db, connect_db, User, Sport, UserSport, League, UserLeague, Team, UserTeam
import requests

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

# Now we can import app
from app import app, CURR_USER, API_BASE_URL

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Wilhelm50@localhost/sports_test'
app.config['SQLALCHEMY_ECHO'] = False
# os.environ['DATABASE_URL'] = "postgresql://postgres:Wilhelm50@localhost/sports_test"

# Make Flask errors to be real errors
app.config['TESTING'] = True

# Create our tables, in each test, we'll delete the data
# and create fresh new clean test data

db.drop_all()
db.create_all()

app.config['WTF_CSRF_ENABLED'] = False

class ViewTestCase(TestCase):
    """Test views."""

    def setUp(self):

        UserTeam.query.delete()
        Team.query.delete()
        db.session.commit()

        UserLeague.query.delete()
        League.query.delete()
        db.session.commit()

        UserSport.query.delete()
        Sport.query.delete()
        db.session.commit()

        User.query.delete()
        db.session.commit()

        self.client = app.test_client()

        self.u1 = User.signup("testuser", "test@test.com", "testuser")
        self.u1.id = 1212

        db.session.add(self.u1)        
        db.session.commit()

        s1 = Sport(id=107, name="American Football")
        s2 = Sport(id=106, name="Basketball")
        s3 = Sport(id=105, name="Baseball")
        
        db.session.add_all([s1, s2, s3]) 
        db.session.commit()

    def test_index(self):
        """Does welcome page show up?"""

        with self.client as c:
            resp = c.get('/')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Welcome to the Sports App!', html)

    def test_index_user(self):
        """Does flash message show when no user?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER] = self.u1.id

            resp = c.get('/', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Pick a favorite sport.', html)
            self.assertIn('American Football', html)
            self.assertIn('Baseball', html)

    def test_home_no_user(self):
        """Does welcome message appear when no user?"""

        with self.client as c:
            resp = c.get('/')
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Welcome to the Sports App!', html)

    def test_home_post(self):
        """Does the sport user picked show and do the
           leagues in this sport show up?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER] = self.u1.id

            d = {"sport": 107, "sportName": "American Football"}
            resp = c.post('/home', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Pick a favorite league', html)
            self.assertIn('American Football', html)
            self.assertIn('NFL', html)

    def test_sport_no_user(self):
        """Does welcome message appear when no user"""

        with self.client as c:
            resp = c.get('/home/addsport', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Welcome to the Sports App!', html)

    def test_sport_post(self):
        """Does the league user picked show up and do the
           teams in this league show up?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER] = self.u1.id
                sess["id_sport"] = 107
                sess["sport_name"] = "American Football"
            
            d = {"league": 4391, "leagueName": 'NFL'}
            resp = c.post('/home/addsport', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Pick a favorite team', html)
            self.assertIn('American Football', html)
            self.assertIn('NFL', html)
            self.assertIn('Dallas Cowboys', html)

    def test_league_no_user(self):
        """Does welcome message appear when no user"""

        with self.client as c:
            resp = c.get('/home/addleague', follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Welcome to the Sports App!', html)

    def test_league_post(self):
        """Does the team user picked show up and are we
           back to picking a sport again?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER] = self.u1.id
                sess["id_sport"] = 107
                sess["sport_name"] = "American Football"
                sess["id_league"] = 4391
                sess["league_name"] = "NFL"
            
            d = {"team": 134934}
            resp = c.post('/home/addleague', data=d, follow_redirects=True)
            html = resp.get_data(as_text=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn('Pick a favorite sport', html)
            self.assertIn('American Football', html)
            self.assertIn('NFL', html)
            self.assertIn('Dallas Cowboys', html)