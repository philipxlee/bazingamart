from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required, current_user
from app.models.orders import Order

bp = Blueprint('orders', __name__)

@bp.route('/view_orders')
@login_required
def view_orders():
    user_id = current_user.id
    orders = Order.get_all_orders(user_id)
    return render_template('view_orders.html', orders=orders)

@bp.route('/order_details/<int:order_id>')
@login_required
def order_details(order_id):
    user_id = current_user.id
    # Verify that the order belongs to the current user
    orders = Order.get_all_orders(user_id)
    if not any(order.order_id == order_id for order in orders):
        flash("Order not found.", "error")
        return redirect(url_for('orders.view_orders'))
    
    order = next(order for order in orders if order.order_id == order_id)
    order_items = Order.get_order_details(order_id)
    return render_template('order_details.html', order=order, order_items=order_items)