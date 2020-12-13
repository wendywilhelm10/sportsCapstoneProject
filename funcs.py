from flask import Flask, session, g
from models import db, User, Sport, UserSport, League, UserLeague, Team, UserTeam
import requests

API_BASE_URL = "https://www.thesportsdb.com/api/v1/json/1"

app = Flask(__name__)


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
                        'twitter': team.twitter, 'facebook': team.facebook, 'instagram': team.instagram, 'website': team.website}
                teams.append(name)

    return teams


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