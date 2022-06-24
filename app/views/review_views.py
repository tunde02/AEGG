from datetime import datetime

from flask import Blueprint, flash, render_template, request, url_for, g
from werkzeug.utils import redirect
from sqlalchemy.sql import func

from app import db
from app.forms import ReviewForm
from app.models import Card, CardReview, Mage, MageReview, Nemesis
from app.views.auth_views import login_required


bp = Blueprint('review', __name__, url_prefix='/review')


def calc_avg_score(score_column, filter):
    new_avg_score = db.session.query(func.avg(score_column).label('avg_score')).filter(filter).first().avg_score
    return float(new_avg_score if new_avg_score else 0)


@bp.before_request
def load_navbar_tab():
    g.navbar_tab = 'wiki'


@bp.route('/create/mage/<int:mage_id>', methods=['GET', 'POST'])
@login_required
def create_mage_review(mage_id):
    form = ReviewForm()
    mage = Mage.query.get_or_404(mage_id)

    if request.method == 'POST' and form.validate_on_submit():
        review = MageReview(
            user=g.user,
            mage=mage,
            content=form.content.data,
            score=int(form.score.data),
            create_date=datetime.now()
        )

        mage.avg_score = calc_avg_score(score_column=MageReview.score,
                                        filter=(MageReview.mage_id == mage.id))

        db.session.add(review)
        db.session.commit()

        return redirect(url_for('wiki.mage_detail', mage_id=mage.id))

    return render_template('review/review_form.html', form=form, wiki_info=mage)


@bp.route('/create/card/<int:card_id>', methods=['GET', 'POST'])
@login_required
def create_card_review(card_id):
    form = ReviewForm()
    card = Card.query.get_or_404(card_id)

    if request.method == 'POST' and form.validate_on_submit():
        review = CardReview(
            user=g.user,
            card=card,
            content=form.content.data,
            score=int(form.score.data),
            create_date=datetime.now()
        )

        card.avg_score = calc_avg_score(score_column=CardReview.score,
                                        filter=(CardReview.card_id == card.id))

        db.session.add(review)
        db.session.commit()

        return redirect(url_for('wiki.card_detail', card_id=card.id))

    return render_template('review/review_form.html', form=form, wiki_info=card)


@bp.route('/create/nemesis/<int:nemesis_id>', methods=['GET', 'POST'])
@login_required
def create_nemesis_review(nemesis_id):
    # TODO
    print('CREATE NEMESIS REVIEW')
    return redirect(url_for('wiki.wiki_list', wiki_type='mage'))


def get_review_info(wiki_type, review_id):
    review_info = {}

    if wiki_type == 'mage':
        review_info['review'] = MageReview.query.get_or_404(review_id)
        review_info['wiki_info'] = review_info['review'].mage
        review_info['score_column'] = MageReview.score
        review_info['filter'] = (MageReview.mage_id == review_info['wiki_info'].id)
        review_info['next_url'] = url_for('wiki.mage_detail', mage_id=review_info['wiki_info'].id)
    elif wiki_type == 'card':
        review_info['review'] = CardReview.query.get_or_404(review_id)
        review_info['wiki_info'] = review_info['review'].card
        review_info['score_column'] = CardReview.score
        review_info['filter'] = (CardReview.card_id == review_info['wiki_info'].id)
        review_info['next_url'] = url_for('wiki.card_detail', card_id=review_info['wiki_info'].id)
    elif wiki_type == 'nemesis':
        # TODO
        pass

    return review_info


@bp.route('/modify/<int:review_id>', methods=['GET', 'POST'])
@login_required
def modify_review(review_id):
    wiki_type = request.args.get('wiki_type', type=str, default='')
    review_info = get_review_info(wiki_type, review_id)

    if 'review' not in review_info.keys():
        return redirect(url_for('wiki.wiki_list', wiki_type='mage'))

    if g.user != review_info['review'].user:
        flash('리뷰 수정 권한이 없습니다.')
        return redirect(review_info['next_url'])

    if request.method == 'POST':
        form = ReviewForm()

        if form.validate_on_submit():
            form.populate_obj(review_info['review'])
            review_info['review'].modify_date = datetime.now()

            review_info['wiki_info'].avg_score = calc_avg_score(score_column=review_info['score_column'], filter=review_info['filter'])

            db.session.commit()

            return redirect(review_info['next_url'])
    else:
        form = ReviewForm(obj=review_info['review'])

    return render_template('review/review_form.html', form=form, wiki_info=review_info['wiki_info'])


@bp.route('/delete/<int:review_id>')
@login_required
def delete_review(review_id):
    wiki_type = request.args.get('wiki_type', type=str, default='')
    review_info = get_review_info(wiki_type, review_id)

    if 'review' not in review_info.keys():
        return redirect(url_for('wiki.wiki_list', wiki_type='mage'))

    if g.user != review_info['review'].user:
        flash('리뷰 삭제 권한이 없습니다.')
    else:
        db.session.delete(review_info['review'])
        review_info['wiki_info'].avg_score = calc_avg_score(score_column=review_info['score_column'], filter=review_info['filter'])
        db.session.commit()

    return redirect(review_info['next_url'])
