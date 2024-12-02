from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.models.cart_items import CartItems
from app.models.cart_submission import CartSubmission
from app.models.coupons import Coupons
from decimal import Decimal

bp = Blueprint('carts', __name__)


@bp.route('/view_cart')
@login_required
def view_cart():
    user_id = current_user.id
    page = request.args.get('page', default=1, type=int)
    per_page = 5
    cart_items, total_items = CartItems.get_all_items(user_id, page, per_page)
    total_pages = (total_items + per_page - 1) // per_page

    total_cost = sum(Decimal(item.quantity) * item.unit_price for item in cart_items)
    coupon_code = request.args.get('coupon_code') or CartItems.get_coupon_code(user_id)
    discount_percentage = 0
    discount_amount = Decimal('0.00')
    
    if coupon_code:
        discount_percentage = Coupons.get_discount(coupon_code) or 0
        discount_rate = Decimal(discount_percentage) / Decimal('100')
        discount_amount = total_cost * discount_rate
        total_cost_after_discount = total_cost - discount_amount
    else:
        total_cost_after_discount = total_cost

    return render_template(
        'view_carts_page.html',
        cart_items=cart_items,
        total_cost=total_cost,
        total_cost_after_discount=total_cost_after_discount,
        discount_percentage=discount_percentage,
        discount_amount=discount_amount,
        coupon_code=coupon_code,
        page=page,
        total_pages=total_pages
    )

@bp.route('/add_to_cart', methods=['POST'])
@login_required
def add_to_cart():
    product_id = request.form.get('product_id', type=int)
    seller_id = request.form.get('seller_id', type=int)
    quantity = request.form.get('quantity', 1, type=int)
    user_id = current_user.id
    result = CartItems.add_item(user_id, product_id, quantity, seller_id)
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
        flash("Updated quantity successfully!", "success")
        return redirect(url_for('carts.view_cart'))
    else:
        flash("Update quantity failed: not enough inventory!", "error")
        return redirect(url_for('carts.view_cart'))

@bp.route('/remove_item', methods=['POST'])
@login_required
def remove_item():
    product_id = request.form.get('product_id', type=int)
    seller_id = request.form.get('seller_id', type=int)
    user_id = current_user.id
    result = CartItems.remove_item(user_id, product_id, seller_id)
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


@bp.route('/apply_coupon', methods=['POST'])
@login_required
def apply_coupon():
    coupon_code = request.form.get('coupon_code')
    user_id = current_user.id
    result = CartItems.apply_coupon_code(user_id, coupon_code)
    if result == "success":
        flash("Coupon code applied successfully!", "success")
    else:
        CartItems.clear_coupon_code(user_id)
        flash(result, "error")
    return redirect(url_for('carts.view_cart'))

@bp.route('/delete_cart', methods=['POST'])
@login_required
def delete_cart():
    user_id = current_user.id
    result = CartItems.delete_cart(user_id)
    if result == "success":
        flash("Cart deleted successfully!", "success")
    else:
        flash("Failed to delete cart.", "error")
    return redirect(url_for('carts.view_cart'))
