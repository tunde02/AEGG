from app import db


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    nickname = db.Column(db.String(200), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    about_me = db.Column(db.String(300), nullable=False, default='')
    profile_image = db.Column(db.String(200), nullable=False, default='images/defaults/profile_image.png')


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
    user = db.relationship('User', backref=db.backref('post_list', passive_deletes=True))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    num_views = db.Column(db.Integer, nullable=False, default=0)
    create_date = db.Column(db.DateTime(), nullable=False)
    modify_date = db.Column(db.DateTime())


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text(), nullable=True)
    user = db.relationship('User', backref=db.backref('comment_list', passive_deletes=True))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    post = db.relationship('Post', backref=db.backref('comment_list', passive_deletes=True))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id', ondelete='CASCADE'), nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('comment.id', ondelete='CASCADE'))
    create_date = db.Column(db.DateTime(), nullable=False)
    modify_date = db.Column(db.DateTime())
    is_deleted = db.Column(db.Boolean, nullable=False, default=False)


related_mage = db.Table(
    'related_mage',
    db.Column('card_id', db.Integer, db.ForeignKey('card.id', ondelete='CASCADE'), primary_key=True),
    db.Column('mage_id', db.Integer, db.ForeignKey('mage.id', ondelete='CASCADE'), primary_key=True)
)

related_nemesis = db.Table(
    'related_nemesis',
    db.Column('card_id', db.Integer, db.ForeignKey('card.id', ondelete='CASCADE'), primary_key=True),
    db.Column('nemesis_id', db.Integer, db.ForeignKey('nemesis.id', ondelete='CASCADE'), primary_key=True)
)


class Card(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    cost = db.Column(db.Integer, nullable=False, default=0)
    effect = db.Column(db.Text(), nullable=False, default='')
    avg_score = db.Column(db.Float(), nullable=False, default=0.0)
    related_mage = db.relationship('Mage', secondary=related_mage, backref=db.backref('related_card_list', passive_deletes=True))
    related_nemesis = db.relationship('Nemesis', secondary=related_nemesis, backref=db.backref('related_card_list', passive_deletes=True))
    image = db.Column(db.String(200), nullable=False, default='images/defaults/card.png')


class CardEN(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card = db.relationship('Card', backref=db.backref('card_en', passive_deletes=True), uselist=False)
    card_id = db.Column(db.Integer, db.ForeignKey('card.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(100), nullable=False)
    effect = db.Column(db.Text(), nullable=False, default='')


class CardReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.relationship('User', backref=db.backref('card_review_list', passive_deletes=True))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    card = db.relationship('Card', backref=db.backref('review_list', passive_deletes=True))
    card_id = db.Column(db.Integer, db.ForeignKey('card.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text(), nullable=False, default='')
    score = db.Column(db.Integer, nullable=False, default=0)
    create_date = db.Column(db.DateTime(), nullable=False)
    modify_date = db.Column(db.DateTime())


class Mage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    series = db.Column(db.String(100), nullable=False, default='에이언즈 엔드')
    ability_name = db.Column(db.String(100), nullable=False, default='')
    ability = db.Column(db.Text(), nullable=False, default='')
    activation_time = db.Column(db.String(100), nullable=False, default='')
    required_charges = db.Column(db.Integer, nullable=False, default=0)
    avg_score = db.Column(db.Float(), nullable=False, default=0.0)
    image = db.Column(db.String(200), nullable=False, default='images/defaults/mage.png')
    board_image = db.Column(db.String(200), nullable=False, default='images/defaults/mage_board.png')
    back_board_image = db.Column(db.String(200), nullable=False, server_default='images/defaults/mage_board.png')


class MageEN(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mage = db.relationship('Mage', backref=db.backref('mage_en', passive_deletes=True), uselist=False)
    mage_id = db.Column(db.Integer, db.ForeignKey('mage.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    series = db.Column(db.String(100), nullable=False, default="Aeon's End")
    ability_name = db.Column(db.String(100), nullable=False, default='')
    ability = db.Column(db.Text(), nullable=False, default='')
    activation_time = db.Column(db.String(100), nullable=False, default='')


class MageStartingHand(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mage = db.mage = db.relationship('Mage', backref=db.backref('starting_hand', passive_deletes=True))
    mage_id = db.Column(db.Integer, db.ForeignKey('mage.id', ondelete='CASCADE'), nullable=False)
    card = db.relationship('Card')
    card_id = db.Column(db.Integer, db.ForeignKey('card.id', ondelete='CASCADE'), nullable=False)
    order = db.Column(db.Integer, nullable=False, default=0)


class MageStartingDeck(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mage = db.mage = db.relationship('Mage', backref=db.backref('starting_deck', passive_deletes=True))
    mage_id = db.Column(db.Integer, db.ForeignKey('mage.id', ondelete='CASCADE'), nullable=False)
    card = db.relationship('Card')
    card_id = db.Column(db.Integer, db.ForeignKey('card.id', ondelete='CASCADE'), nullable=False)
    order = db.Column(db.Integer, nullable=False, default=0)


class MageSpecificCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mage = db.mage = db.relationship('Mage', backref=db.backref('specific_card_list', passive_deletes=True))
    mage_id = db.Column(db.Integer, db.ForeignKey('mage.id', ondelete='CASCADE'), nullable=False)
    card = db.relationship('Card')
    card_id = db.Column(db.Integer, db.ForeignKey('card.id', ondelete='CASCADE'), nullable=False)
    label = db.Column(db.String(100), nullable=False, default='')

class MageSpecificObject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mage = db.mage = db.relationship('Mage', backref=db.backref('specific_obj_list', passive_deletes=True))
    mage_id = db.Column(db.Integer, db.ForeignKey('mage.id', ondelete='CASCADE'), nullable=False)
    label = db.Column(db.String(100), nullable=False, default='')
    image = db.Column(db.String(200), nullable=False, default='images/defaults/mage_specific.png')


class MageReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.relationship('User', backref=db.backref('mage_review_list', passive_deletes=True))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    mage = db.relationship('Mage', backref=db.backref('review_list', passive_deletes=True))
    mage_id = db.Column(db.Integer, db.ForeignKey('mage.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text(), nullable=False, default='')
    score = db.Column(db.Integer, nullable=False, default=0)
    create_date = db.Column(db.DateTime(), nullable=False)
    modify_date = db.Column(db.DateTime())


class Nemesis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    series = db.Column(db.String(100), nullable=False, default='에이언즈 엔드')
    tier = db.Column(db.Integer, nullable=False, default=0)
    difficulty = db.Column(db.Integer, nullable=False, default=0)
    hp = db.Column(db.Integer, nullable=False, default=0)
    setup = db.Column(db.Text(), nullable=False, default='')
    additional_rules = db.Column(db.Text(), nullable=False, default='')
    unleash = db.Column(db.Text(), nullable=False, default='')
    increased_diff = db.Column(db.Text(), nullable=False, default='')
    avg_score = db.Column(db.Float(), nullable=False, default=0.0)
    image = db.Column(db.String(200), nullable=False, default='images/defaults/nemesis.png')
    board_image = db.Column(db.String(200), nullable=False, default='images/defaults/nemesis_board.png')
    back_board_image = db.Column(db.String(200), nullable=False, default='images/defaults/nemesis_board.png')


class NemesisEN(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nemesis = db.relationship('Nemesis', backref=db.backref('nemesis_en', passive_deletes=True), uselist=False)
    nemesis_id = db.Column(db.Integer, db.ForeignKey('nemesis.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    series = db.Column(db.String(100), nullable=False, default="Aeon's End")
    setup = db.Column(db.Text(), nullable=False, default='')
    additional_rules = db.Column(db.Text(), nullable=False, default='')
    unleash = db.Column(db.Text(), nullable=False, default='')
    increased_diff = db.Column(db.Text(), nullable=False, default='')


class NemesisCardInfo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card = db.relationship('Card', backref=db.backref('nemesis_card_info', passive_deletes=True), uselist=False)
    card_id = db.Column(db.Integer, db.ForeignKey('card.id', ondelete='CASCADE'), nullable=False)
    tier = db.Column(db.Integer, nullable=False, default=0)
    hp = db.Column(db.Integer, nullable=False, default=0)


class NemesisSpecificCard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nemesis = db.relationship('Nemesis', backref=db.backref('specific_card_list', passive_deletes=True))
    nemesis_id = db.Column(db.Integer, db.ForeignKey('nemesis.id', ondelete='CASCADE'), nullable=False)
    card = db.relationship('Card')
    card_id = db.Column(db.Integer, db.ForeignKey('card.id', ondelete='CASCADE'), nullable=False)
    label = db.Column(db.String(100), nullable=False, default='')


class NemesisSpecificObject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nemesis = db.relationship('Nemesis', backref=db.backref('nemesis_specific_obj_list', passive_deletes=True))
    nemesis_id = db.Column(db.Integer, db.ForeignKey('nemesis.id', ondelete='CASCADE'), nullable=False)
    label = db.Column(db.String(100), nullable=False, default='')
    image = db.Column(db.String(200), nullable=False, default='images/defaults/specific.png')


class NemesisReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.relationship('User', backref=db.backref('nemesis_review_list', passive_deletes=True))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    nemesis = db.relationship('Nemesis', backref=db.backref('review_list', passive_deletes=True))
    nemesis_id = db.Column(db.Integer, db.ForeignKey('nemesis.id', ondelete='CASCADE'), nullable=False)
    content = db.Column(db.Text(), nullable=False, default='')
    score = db.Column(db.Integer, nullable=False, default=0)
    create_date = db.Column(db.DateTime(), nullable=False)
    modify_date = db.Column(db.DateTime())
