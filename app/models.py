from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    nickname = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    about_me = db.Column(db.String(300), nullable=False, default='')
    profile_image = db.Column(db.String(200), nullable=False, default='images/profile/default.png')


post_voter = db.Table(
    'post_voter',
    db.Column('post_id', db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), primary_key=True)
)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(20), nullable=False)
    content = db.Column(db.Text(), nullable=False)
    voter = db.relationship('User', secondary=post_voter, backref=db.backref('voted_post_list', passive_deletes=True))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    user = db.relationship('User', backref=db.backref('post_list', passive_deletes=True))
    num_views = db.Column(db.Integer, nullable=False, default=0)
    create_date = db.Column(db.DateTime(), nullable=False)
    modify_date = db.Column(db.DateTime())
