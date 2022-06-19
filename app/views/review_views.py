from datetime import datetime

from flask import Blueprint, render_template, request, url_for, g
from werkzeug.utils import redirect

from app import db
from app.forms import ReviewForm
from app.models import Card, CardReview, Mage, Nemesis
from app.views.auth_views import login_required


bp = Blueprint('review', __name__, url_prefix='/review')


@bp.before_request
def load_navbar_tab():
    g.navbar_tab = 'wiki'


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

        card.avg_score = (card.avg_score * (len(card.review_list) - 1) + review.score) / len(card.review_list)

        db.session.add(review)
        db.session.commit()

        return redirect(url_for('wiki.card_detail', card_id=card.id))

    return render_template('review/review_form.html', form=form, card=card)


@bp.route('/delete/card/<int:review_id>', methods=['GET', 'POST'])
@login_required
def delete_card_review(review_id):
    # TODO
    print('Delete Card Review')

    return redirect(url_for('wiki.card_list'))


@bp.route('/modify/card/<int:review_id>', methods=['GET', 'POST'])
@login_required
def modify_card_review(review_id):
    # TODO
    print('Modify Card Review')

    return redirect(url_for('wiki.card_list'))
