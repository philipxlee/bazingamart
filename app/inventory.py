from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from app.models.inventory_items import InventoryItems

bp = Blueprint('inventory', __name__)

@bp.route('/view_inventory')
@login_required
def view_inventory():
    """
    Displays the seller's inventory items.
    """
    seller_id = current_user.id
    # Use the helper method to retrieve all inventory items for the seller
    inventory_items = InventoryItems.get_all_by_user(seller_id)
    return render_template('view_inventory_page.html', inventory_items=inventory_items)

@bp.route('/fulfillment_center')
@login_required
def fulfillment_center():
    """
    Displays the seller's order history and fulfillment status for each item.
    """
    seller_id = current_user.id
    # Use the helper method to retrieve all orders associated with the seller's products
    orders = InventoryItems.get_seller_orders(seller_id)
    return render_template('view_fulfillment_center.html', orders=orders)

@bp.route('/fulfill_item', methods=['POST'])
@login_required
def fulfill_item():
    """
    Marks a specific item in an order as fulfilled.
    """
    seller_id = current_user.id
    order_id = request.form.get('order_id')
    product_id = request.form.get('product_id')

    # Ensure that the item belongs to the seller before marking it as fulfilled
    item_belongs_to_seller = current_app.db.execute('''
        SELECT 1 
        FROM CartProducts cp
        JOIN Products p ON cp.product_id = p.id
        WHERE cp.order_id = :order_id AND cp.product_id = :product_id AND p.seller_id = :seller_id
    ''', order_id=order_id, product_id=product_id, seller_id=seller_id)
    
    if not item_belongs_to_seller:
        flash("Unauthorized action.", "error")
        return redirect(url_for('inventory.fulfillment_center'))
    
    # Update the fulfillment status of the item to 'Fulfilled'
    rows_updated = current_app.db.execute('''
        UPDATE CartProducts
        SET fulfillment_status = 'Fulfilled'
        WHERE order_id = :order_id AND product_id = :product_id
    ''', order_id=order_id, product_id=product_id)
    
    if rows_updated:
        flash("Item marked as fulfilled.", "success")
    else:
        flash("Error marking item as fulfilled.", "error")
    
    return redirect(url_for('inventory.fulfillment_center'))