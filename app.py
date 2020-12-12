"""Flask app for Sports Teams"""
from flask import Flask, request, render_template, flash, session, redirect, g, json
from models import db, connect_db, User, Sport, UserSport, League, UserLeague, Team, UserTeam
from sqlalchemy.exc import IntegrityError

from forms import UserAddForm, UserForm, AddSportForm, AddLeagueForm, AddTeamForm
import requests

CURR_USER = "curr_user"
API_BASE_URL = "https://www.thesportsdb.com/api/v1/json/1"

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///sports_db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Wilhelm50@localhost/sports_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True
app.config['SECRET_KEY'] = 'mysecretsports'

connect_db(app)

# db.drop_all()
# db.create_all()


@app.before_request
def add_user_to_g():
    """If we're logged in, add curr user to Flask global."""

    if CURR_USER in session:
        g.user = User.query.get(session[CURR_USER])
    else:
        g.user = None


@app.route('/')
def index_page():

    if not g.user:
        return render_template('index.html')

    return redirect('/home')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    """Handle user signup"""

    form = UserAddForm()

    if form.validate_on_submit():
        try:
            user = User.signup(
                username=form.username.data,
                password=form.password.data,
                email=form.email.data   
            )
            db.session.commit()

        except IntegrityError:
            form.username.errors.append('Username taken.  Please pick another name.')
            form.email.errors.append('Email taken.  Please pick another email.')
            return render_template('signup.html', form=form)

        session[CURR_USER] = user.id
        g.user = user
        return redirect('/home')

    else:
        return render_template('signup.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""

    form = UserForm()

    if form.validate_on_submit():
        username = form.username.data     
        password = form.password.data   

        user = User.authenticate(username, password)
        if user:
            flash(f'Welcome back {user.username}!', 'primary')
            session[CURR_USER] = user.id
            g.user = user
            return redirect('/home')

        flash('Invalid credentials.', 'danger')

    return render_template('login.html', form=form)


@app.route('/home', methods=['GET', 'POST'])
def home_page():

    if not g.user:
        flash('You are not logged in', 'danger')
        return redirect('/')

    form = AddSportForm()

    if request.method == 'POST':
        id_sport = form.sport.data
        sport_name = form.sportName.data
        session['id_sport'] = id_sport
        session['sport_name'] = sport_name

        return redirect('/home/addsport')

    form.sport.choices = (db.session.query(Sport.id, Sport.name).order_by(Sport.name).all())
    sports = get_teams_following()

    return render_template('home.html', form=form, sports=sports)


@app.route('/home/addsport', methods=['GET', 'POST'])
def add_sport():

    if not g.user:
        flash('You are not logged in', 'danger')
        return redirect('/')

    form = AddLeagueForm()
    sport = session['sport_name']

    if request.method == 'POST':
        id_league = form.league.data   
        league_name = form.leagueName.data
        session['id_league'] = id_league
        session['league_name'] = league_name

        return redirect('/home/addleague')

    res = requests.get(f'{API_BASE_URL}/all_leagues.php')
    data = res.json()
    leagues = data['leagues']
    sport_leagues = get_leagues(leagues, sport)

    form.league.choices = sport_leagues
    sports = get_teams_following()
    return render_template('sport.html', form=form, sport=sport, sports=sports)


@app.route('/home/addleague', methods=['GET', 'POST'])
def add_league():

    if not g.user:
        flash('You are not logged in', 'danger')
        return redirect('/')

    form = AddTeamForm()
    sport = session['sport_name']
    league = session['league_name']

    if request.method == 'POST':
        id_team = form.team.data
        session['id_team'] = id_team

        add_team()
        return redirect('/home')

    res = requests.get(f'{API_BASE_URL}/search_all_teams.php?l={league}')
    data = res.json()
    teams = data['teams']
    league_teams = get_teams(teams, league)

    form.team.choices = league_teams
    sports = get_teams_following()
    return render_template('league.html', form=form, sport=sport, league=league, sports=sports)


@app.route('/home/user_team', methods=['GET', 'POST'])
def show_team():

    if not g.user:
        flash('You are not logged in', 'danger')
        return redirect('/')

    # import pdb
    # pdb.set_trace()

    user_team_id = request.form['user_team_id']

    user_team = UserTeam.query.get_or_404(user_team_id)
    team = Team.query.get_or_404(user_team.team_api_id)

    res = requests.get(f'{API_BASE_URL}/lookupteam.php?id={team.id}')
    data = res.json()
    team_info = data['teams']

    res = requests.get(f'{API_BASE_URL}/eventslast.php?id={team.id}')
    data = res.json()
    last_five = data['results']

    res = requests.get(f'{API_BASE_URL}/eventsnext.php?id={team.id}')
    data = res.json()
    next_five = data['events']

    return render_template('team.html', team=team, last_five=last_five, next_five=next_five, team_info=team_info, user_team=user_team)


@app.route('/logout')
def logout():
    """Logout user."""

    if CURR_USER in session:
        del session[CURR_USER]
        session.pop('id_sport', None)
        session.pop('id_league', None)
        session.pop('sport', None)
        return redirect('/')


@app.route('/api/team/<int:id>', methods=['DELETE'])
def delete_team(id):
    user_team = UserTeam.query.get_or_404(id)
    print('**********************')
    print(user_team.team_api_id)
    print(user_team.user_league_id)

    db.session.delete(user_team)
    db.session.commit()
    print('delete this team from the user_teams table')

    cnt = UserTeam.query.filter(UserTeam.team_api_id==f'{user_team.team_api_id}').count()
    if cnt == 0:
        team = Team.query.get_or_404(user_team.team_api_id)
        db.session.delete(team)
        db.session.commit()
        print('deleted team from teams table')

    cnt = UserTeam.query.filter(UserTeam.user_league_id==f'{user_team.user_league_id}').count()
    if cnt == 0:
        user_league = UserLeague.query.get_or_404(user_team.user_league_id)
        db.session.delete(user_league)
        db.session.commit()
        print('delete league from user_leagues table')
    else:
        user_league = UserLeague.query.get_or_404(user_team.user_league_id)

    cnt = UserLeague.query.filter(UserLeague.league_api_id==f'{user_league.league_api_id}').count()
    if cnt == 0:
        league = League.query.get_or_404(user_league.league_api_id)
        db.session.delete(league)
        db.session.commit()
        print('delete league from leagues table')

    return("deleted")


@app.route('/api/save/<int:id>', methods=['POST'])
def save_note(id):
    req = json.loads(request.data)
    notes = req['notes']

    user_team = UserTeam.query.get_or_404(id)
    user_team.notes = notes
    db.session.add(user_team)
    db.session.commit()

    return("saved")


def get_leagues(leagues, sport):
    sport_leagues = []

    for league in leagues:
        if league['strSport'] == sport:
            tup = (league['idLeague'], league['strLeague'])
            sport_leagues.append(tup)

    return sport_leagues


def get_teams(teams, league):
    league_teams = []
    user_teams = []

    id_sport = session['id_sport']
    id_league = session['id_league']

    user_id = UserSport.query.filter((UserSport.sport_api_id==f'{id_sport}') & (UserSport.user_id==f'{g.user.id}')).first()
    
    if user_id:
        league_id = UserLeague.query.filter((UserLeague.league_api_id==f'{id_league}') & (UserLeague.user_sport_id==f'{user_id.id}')).first()

        if league_id:
            user_teams = UserTeam.query.filter(UserTeam.user_league_id==f'{league_id.id}').all()

    # import pdb
    # pdb.set_trace()

    for team in teams:
        add_to_list = True
        for ut in user_teams:
            if ut.team_api_id == int(team['idTeam']):
                add_to_list = False
                break;

        if add_to_list:
            tup = (team['idTeam'], team['strTeam'])
            league_teams.append(tup)

    return league_teams


def add_team():
    id_sport = session['id_sport']
    id_league = session['id_league']
    league_name = session['league_name']
    id_team = session['id_team']

    user_sport = UserSport.query.filter((UserSport.sport_api_id==f'{id_sport}') & (UserSport.user_id==f'{g.user.id}')).all()
    if not user_sport:
        user_sport = UserSport(sport_api_id=id_sport, user_id=g.user.id)
        db.session.add(user_sport)
        db.session.commit()
        user_sport_id = user_sport.id
    else:
        user_sport_id = user_sport[0].id

    cnt = League.query.filter(League.id==f'{id_league}').count()
    if cnt == 0:
        league = League(id=id_league, name=league_name)
        db.session.add(league)
        db.session.commit()

    user_league = UserLeague.query.filter((UserLeague.league_api_id==f'{id_league}') & (UserLeague.user_sport_id==f'{user_sport_id}')).all()

    if cnt == 0 or not user_league:
        user_league = UserLeague(league_api_id=id_league, user_sport_id=user_sport_id)
        db.session.add(user_league)
        db.session.commit()
        user_league_id = user_league.id
    else:
        user_league_id = user_league[0].id

    cnt = Team.query.filter(Team.id==f'{id_team}').count()
    if cnt == 0:
        res = requests.get(f'{API_BASE_URL}/lookupteam.php?id={id_team}')
        data = res.json()
        team = data['teams'][0]

        team_name = team['strTeam']
        stadium = team['strStadium']
        stadium_loc = team['strStadiumLocation']
        if not team['intStadiumCapacity']:
            stadium_cap = None
        else:
            stadium_cap = int(team['intStadiumCapacity'])
        website = team['strWebsite']
        facebook = team['strFacebook']
        twitter = team['strTwitter']
        instagram = team['strInstagram']
        logo_pic = team['strTeamLogo']

        if logo_pic == None:
            logo_pic = team['strTeamBadge']
            if logo_pic == None:
                logo_pic = team['strTeamJersey']

        team = Team(id=id_team, name=team_name, stadium_name=stadium, stadium_loc=stadium_loc,
                    stadium_cap=stadium_cap, website=website, facebook=facebook, twitter=twitter, 
                    instagram=instagram, logo_pic=logo_pic)
        db.session.add(team)
        db.session.commit()
    else:
        team = Team.query.get_or_404(id_team)

    user_team = UserTeam(team_api_id=team.id, user_league_id=user_league_id)
    db.session.add(user_team)
    db.session.commit()


def get_teams_following():
    all_teams = []
    teams = []

    sports = Sport.query.join(UserSport).filter(UserSport.user_id==f'{g.user.id}').all()
    
    for sport in sports:
        user_sport = UserSport.query.filter((UserSport.sport_api_id==f'{sport.id}') & (UserSport.user_id==f'{g.user.id}')).first()
        leagues = League.query.join(UserLeague).filter(UserLeague.user_sport_id==f'{user_sport.id}').all()
        
        for league in leagues:
            user_league = UserLeague.query.filter((UserLeague.league_api_id==f'{league.id}') & (UserLeague.user_sport_id==f'{user_sport.id}')).first()
            user_teams = UserTeam.query.filter(UserTeam.user_league_id==f'{user_league.id}').all()
            
            for ut in user_teams:
                team = Team.query.filter(Team.id==f'{ut.team_api_id}').first()
                if team.stadium_name and team.stadium_loc and team.stadium_cap:
                    stadium = 'play in ' + team.stadium_name + ' in ' + team.stadium_loc + ' with a capacity of ' + str(team.stadium_cap) + '.'
                else:
                    stadium = ''
                name = {'userteam': ut.id, 'sport': sport.name, 'league': league.name, 'team': team.name, 'team_logo': team.logo_pic, 'stadium': stadium,
                        'twitter': team.twitter, 'facebook': team.facebook, 'instagram': team.instagram}
                teams.append(name)

    return teams

