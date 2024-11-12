from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.models.orders import Order

bp = Blueprint('orders', __name__)

@bp.route('/view_orders')
@login_required
def view_orders():
    user_id = current_user.id
    page = request.args.get('page', default=1, type=int)
    per_page = 5
    orders = Order.get_all_orders(user_id, page, per_page)
    total_orders = Order.count_orders(user_id)
    total_pages = (total_orders + per_page - 1) // per_page

    return render_template('view_orders.html', orders=orders, page=page, total_pages=total_pages)

@bp.route('/order_details/<int:order_id>')
@login_required
def order_details(order_id):
    user_id = current_user.id
    order = Order.get_order(user_id, order_id)
    if not order:
        flash("Order not found.", "error")
        return redirect(url_for('users.user_home'))
    order_items = Order.get_order_details(order_id)
    return render_template('order_details.html', order=order, order_items=order_items)