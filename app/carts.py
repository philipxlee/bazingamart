from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.models.cart_items import CartItems
from app.models.cart_submission import CartSubmission

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
        flash("Item successfully added to cart!", "success")
    else:
        flash("Failed to add item to cart.", "error")
    
    return redirect(url_for('index.index', product_id=product_id))

@bp.route('/update_quantity', methods=['POST'])
@login_required
def update_quantity():
    product_id = request.form.get('product_id', type=int)
    new_quantity = request.form.get('quantity', type=int)
    user_id = current_user.id
    result = CartItems.update_item_quantity(user_id, product_id, new_quantity)
    if result == "success":
        return redirect(url_for('carts.view_cart'))
    else:
        return result, 500  

@bp.route('/remove_item', methods=['POST'])
@login_required
def remove_item():
    product_id = request.form.get('product_id', type=int)
    user_id = current_user.id
    result = CartItems.remove_item(user_id, product_id)
    if result == "success":
        return redirect(url_for('carts.view_cart'))
    else:
        return result, 500 

@bp.route('/submit_cart', methods=['POST'])
@login_required
def submit_cart():
    result = CartSubmission.submit_cart(current_user.id)
    if result == "Purchase successful!":
        flash("Your purchase was completed successfully!")
    else:
        flash(result)
    return redirect(url_for('carts.view_cart'))
