from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    nickname = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    about_me = db.Column(db.String(300), nullable=False, default='')
    profile_image = db.Column(db.String(200), nullable=False, default='images/profile/default.png')
