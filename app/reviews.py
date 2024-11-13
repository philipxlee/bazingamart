from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from .models.product import Product
from .models.user import User
from .models.reviews import Reviews
from flask import Blueprint
from app.models.orders import Order

bp = Blueprint('orders', __name__)
bp = Blueprint('reviews', __name__)


@bp.route('/search_user_feedback', methods=['GET', 'POST'])
def search_user_feedback():
   """Displays recent feedback for a specified user ID."""
   if request.method == 'POST':
       user_id = int(request.form['user_id'])
       recent_feedback = Reviews.get_recent_feedback(user_id, limit=5)
       return render_template('feedback.html', recent_feedback=recent_feedback, user_id=user_id)
   return render_template('feedback.html')


@bp.route('/add_review', methods=['POST'])
@login_required
def add_review():
   """Handles adding a new review."""
   user_id = current_user.id
   reviewer_type = request.form['reviewer_type']
   product_id = int(request.form['product_id'])
   stars = int(request.form['stars'])
   review_text = request.form['review_text']
   images = request.form.get('images')

   review_id = Reviews.add_review(user_id, reviewer_type, product_id, stars, review_text, images)
   if review_id:
       flash('Review added successfully!', 'success')
   else:
       flash('Error while adding review', 'danger')
   return redirect(url_for('reviews.search_user_feedback'))


@bp.route('/update_review', methods=['POST'])
@login_required
def update_review():
   """Handles updating an existing review."""
   review_id = int(request.form['review_id'])
   stars = int(request.form['stars'])
   review_text = request.form['review_text']
   images = request.form.get('images')


   success = Reviews.update_review(review_id, stars, review_text, images)
   if success:
       flash('Review updated successfully!', 'success')
   else:
       flash('Failed to update review.', 'danger')
   return redirect(url_for('reviews.search_user_feedback'))


@bp.route('/delete_review', methods=['POST'])
@login_required
def delete_review():
   """Handles deleting a review."""
   review_id = int(request.form['review_id'])
   success = Reviews.delete_review(review_id)
   if success:
       flash('Review deleted successfully!', 'success')
   else:
       flash('Failed to delete review.', 'danger')
   return redirect(url_for('reviews.search_user_feedback'))


@bp.route('/upvote_review', methods=['POST'])
@login_required
def upvote_review():
   """Handles upvoting a review."""
   review_id = int(request.form['review_id'])
   success = Reviews.upvote_review(review_id)
   if success:
       flash('Review upvoted successfully!', 'success')
   else:
       flash('Failed to upvote review.', 'danger')
   return redirect(url_for('reviews.search_user_feedback'))


