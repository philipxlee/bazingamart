from flask import render_template, request, redirect, url_for, flash
from flask_login import current_user, login_required
from .models.product import Product
from .models.user import User
from .models.reviews import Reviews
from flask import Blueprint

bp = Blueprint('reviews', __name__)


@bp.route('/search_user_feedback', methods=['GET', 'POST'])
def search_user_feedback():
   """Displays recent feedback for a specified user ID."""
   if request.method == 'POST':
       user_id = int(request.form['user_id'])
       recent_feedback = Reviews.get_recent_feedback(user_id, limit=5)
       return render_template('feedback.html', recent_feedback=recent_feedback, user_id=user_id)
   return render_template('feedback.html')

@bp.route('/product_reviews/<int:product_id>', methods=['GET'])
def product_reviews(product_id):
    """Displays reviews for a specific product."""
    reviews = Reviews.get_reviews_for_product(product_id)
    product = Product.get_product_by_id(product_id)
    if not product:
        flash('Product not found!', 'danger')
        return redirect(url_for('main.index'))  # Redirect to home or main page

    return render_template('product_reviews.html', reviews=reviews, product=product)

@bp.route('/add_review', methods=['POST'])
def add_review():
    """Handles adding a new review."""
    user_id = current_user.id  # Get the current user ID
    product_id = int(request.form['product_id'])  # Get the product ID from the form
    stars = int(request.form['stars'])  # Get the rating (stars) from the form
    review_text = request.form['review_text']  # Get the review text from the form

    # Fetch the product to get the seller_id
    product = Product.get(product_id)  # Assuming Product.get() fetches the product details
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('products.product_detail', product_id=product_id))  # Adjusted for blueprint

    # Get the seller_id from the product
    seller_id = product.seller_id

    # Check if the user has already reviewed the product
    existing_review = Reviews.get_review_by_user_and_product(user_id, product_id)
    if existing_review:
        flash("You have already reviewed this product.", "danger")
        return redirect(url_for('products.seller_detail', product_id=product_id, seller_id=seller_id))  # Adjusted for blueprint

    # Add the new review, passing the seller_id
    review_id = Reviews.add_review(user_id, product_id, stars, review_text, seller_id)
    if review_id:
        flash('Review added successfully!', 'success')
    else:
        flash('Error while adding review', 'danger')

    return redirect(url_for('products.seller_detail', product_id=product_id, seller_id=seller_id))  # Adjusted for blueprint


@bp.route('/edit_review/<int:review_id>', methods=['GET', 'POST'])
@login_required
def edit_review(review_id):
    review = Reviews.get(review_id)
    next_page = request.args.get('next')  # Get the next page from the query parameters
    
    if request.method == 'POST':
        stars = request.form.get('stars')
        review_text = request.form.get('review_text')
        if not stars or not review_text:
            flash("Please provide both a rating (1-5) and a review text.")
            return redirect(url_for('reviews.edit_review', review_id=review_id, next=next_page))
        try:
            stars = int(stars)
            if stars < 1 or stars > 5:
                flash("Stars rating must be between 1 and 5.")
                return redirect(url_for('reviews.edit_review', review_id=review_id, next=next_page))
        except ValueError:
            flash("Invalid stars rating. Please enter a number between 1 and 5.")
            return redirect(url_for('reviews.edit_review', review_id=review_id, next=next_page))

        if Reviews.edit_review(review_id, stars, review_text):
            flash('Review updated successfully!')
            return redirect(next_page if next_page else url_for('users.user_public_view', id=current_user.id))
        else:
            flash('There was an error updating your review.')

    return render_template('edit_review.html', review=review)




@bp.route('/delete_review/<int:review_id>', methods=['POST'])
def delete_review(review_id):
    """Handles deleting a review."""
    user_id = current_user.id  # Get the current user ID

    # Check if the review exists and belongs to the current user
    review = Reviews.get_review_by_id(review_id)
    if not review:
        flash("Review not found.", "danger")
        return redirect(request.referrer)

    if review.user_id != user_id:
        flash("You are not authorized to delete this review.", "danger")
        return redirect(request.referrer)

    # Delete the review
    success = Reviews.delete_review(review_id)
    if success:
        flash("Review deleted successfully!", "success")
    else:
        flash("Error while deleting review.", "danger")

    return redirect(request.referrer)

@bp.route('/seller/<int:seller_id>', methods=['GET', 'POST'])
@login_required
def review_seller(seller_id):
    if request.method == 'POST':
        stars = request.form.get('stars')
        review_text = request.form.get('review_text', '').strip()
        order_id = request.args.get('order_id')  # Retrieve order_id from query parameters

        if not order_id:
            flash("Review submitted", "danger")
            return redirect(url_for('index.index'))

        if stars is None:
            flash("Please select a valid rating.", "danger")
            return redirect(request.url)

        try:
            stars = int(stars)
            if not 1 <= stars <= 5:
                flash("Rating must be between 1 and 5 stars.", "danger")
                return redirect(request.url)
        except ValueError:
            flash("Invalid rating provided.", "danger")
            return redirect(request.url)

        # Insert the review into the database
        try:
            current_app.db.execute("""
                INSERT INTO Reviews (user_id, product_id, seller_id, stars, review_text, review_type, review_date)
                VALUES (:user_id, NULL, :seller_id, :stars, :review_text, 'seller', NOW())
            """, 
            user_id=current_user.id,
            seller_id=seller_id,
            stars=stars,
            review_text=review_text)

            flash("Your review has been submitted successfully!", "success")
        except Exception as e:
            print(f"Error while adding seller review: {e}")
            flash("An error occurred while submitting your review.", "danger")
        
        # Redirect back to the order details page
        return redirect(url_for('orders.order_details', order_id=order_id))

    # Render review form
    return render_template('review_seller.html', seller_id=seller_id)



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


