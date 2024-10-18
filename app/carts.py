from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app.models.cart_items import CartItems

bp = Blueprint('carts', __name__)

@bp.route('/view_cart')
@login_required
def view_cart():
    user_id = current_user.id
    cart_items = CartItems.get_all_items(user_id)
    return render_template('view_carts_page.html', cart_items=cart_items)


@bp.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    product_id = request.form.get('product_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)
    user_id = current_user.id
    result = CartItems.add_item(user_id, product_id, quantity)
    if result == "success":
        return redirect(url_for('carts.view_cart'))
    else:
        return "Failed to add item to cart", 500

"""
Commented out code below is for the version where the product_id is passed as a URL parameter
instead of as a form parameter.
Waiting on Products to be implemented before this can be used.

@bp.route('/add_to_cart/<int:product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    quantity = request.form.get('quantity', 1, type=int)
    user_id = current_user.id
    result = CartItems.add_item(user_id, product_id, quantity)
    if result == "success":
        return redirect(url_for('carts.view_cart'))
    else:
        return "Failed to add item to cart", 500
"""