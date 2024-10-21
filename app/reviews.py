from flask import render_template
from flask_login import current_user
from flask import request

import datetime

from .models.product import Product
from .models.user import User
from .models.reviews import Reviews

from flask import Blueprint
bp = Blueprint('reviews', __name__)

@bp.route('/search_user_feedback', methods=['GET', 'POST'])
def search_user_feedback():
    if request.method == 'POST':
        user_id = int(request.form['user_id'])  # Get the user ID entered by the user
        recent_feedback = Reviews.get_recent_feedback(user_id, limit=5)
        return render_template('feedback_by_id.html',
                               recent_feedback=recent_feedback,
                               user_id=user_id)
    return render_template('feedback_by_id.html')
