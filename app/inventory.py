from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from app.models.inventory_items import InventoryItems
from app.models.orders import Order
from app.models.helpers.db_exceptions_wrapper import handle_db_exceptions

bp = Blueprint('inventory', __name__)

@bp.route('/view_inventory')
@login_required
def view_inventory():
    """
    Displays the seller's inventory items with pagination.
    """
    seller_id = current_user.id
    page = request.args.get('page', 1, type=int)
    items_per_page = 15

    # Use the helper method to retrieve paginated inventory items for the seller
    inventory_items = InventoryItems.get_paginated_by_user(seller_id, page, items_per_page)
    total_items = InventoryItems.get_count_by_user(seller_id)
    total_pages = (total_items + items_per_page - 1) // items_per_page

    return render_template('view_inventory_page.html', inventory_items=inventory_items, page=page, total_pages=total_pages)

# Updated route to view details of a specific inventory item
@bp.route('/view_inventory_item/<int:product_id>', methods=['GET'])
@login_required
def view_inventory_item(product_id):
    """
    Displays detailed information for a specific product in the seller's inventory.
    """
    seller_id = current_user.id
    inventory_item = InventoryItems.get_detailed_inventory_item(seller_id, product_id)
    if not inventory_item:
        flash("Item not found in your inventory.", "error")
        return redirect(url_for('inventory.view_inventory'))

    return render_template('view_inventory_item.html', inventory_item=inventory_item)

# Updated route to update the quantity of an inventory item
@bp.route('/update_inventory_item', methods=['POST'])
@login_required
def update_inventory_item():
    """
    Updates the quantity of a product in the seller's inventory.
    """
    seller_id = current_user.id
    product_id = request.form.get('product_id', type=int)
    new_quantity = request.form.get('new_quantity', type=int)

    InventoryItems.update_inventory_item_quantity(seller_id, product_id, new_quantity)
    flash("Item quantity updated successfully.", "success")
    return redirect(url_for('inventory.view_inventory_item', product_id=product_id))

# Added route to update the price of an inventory item
@bp.route('/update_inventory_item_price', methods=['POST'])
@login_required
def update_inventory_item_price():
    """
    Updates the price of a product in the seller's inventory.
    """
    seller_id = current_user.id
    product_id = request.form.get('product_id', type=int)
    new_price = request.form.get('new_price', type=float)

    InventoryItems.update_inventory_item_price(seller_id, product_id, new_price)
    flash("Item price updated successfully.", "success")
    return redirect(url_for('inventory.view_inventory_item', product_id=product_id))

# Added route to delete an inventory item
@bp.route('/delete_inventory_item', methods=['POST'])
@login_required
def delete_inventory_item():
    """
    Deletes a product from the seller's inventory.
    """
    seller_id = current_user.id
    product_id = request.form.get('product_id', type=int)

    InventoryItems.delete_inventory_item(seller_id, product_id)
    flash("Item removed from inventory successfully.", "success")
    return redirect(url_for('inventory.view_inventory'))

@bp.route('/fulfillment_center')
@login_required
def fulfillment_center():
    """
    Displays the seller's order history and fulfillment status for each item.
    """
    seller_id = current_user.id
    # Use the helper method to retrieve all orders associated with the seller's products
    orders = InventoryItems.get_seller_orders(seller_id)
    return render_template('view_fulfillment_center.html', orders=orders if isinstance(orders, list) else list(orders))