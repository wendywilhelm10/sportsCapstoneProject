from app import app
from models import db, Sport
import requests

# print('going to drop all tables')
db.drop_all()
db.create_all()

def load_sports():
    resp = requests.get('https://www.thesportsdb.com/api/v1/json/1/all_sports.php')
    data = resp.json()
    all_sports = data['sports']

    for sport in all_sports:
        id = sport['idSport']
        name = sport['strSport']
        new_sport = Sport(id=id, name=name)
        
        db.session.add(new_sport)
        db.session.commit()


load_sports()