from flask import Blueprint, render_template, redirect, url_for, request, flash, current_app
from flask_login import login_required, current_user
from app.models.orders import Order 
from app.models.inventory_items import InventoryItems
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

@bp.route('/delete_inventory_item', methods=['POST'])
@login_required
def delete_inventory_item():
    """
    Marks a product as unavailable in the seller's inventory instead of deleting it.
    """
    seller_id = current_user.id
    product_id = request.form.get('product_id', type=int)

    InventoryItems.mark_inventory_item_unavailable(seller_id, product_id)
    flash("Item removed from inventory successfully.", "success")
    return redirect(url_for('inventory.view_inventory'))

""" @bp.route('/add_inventory_item', methods=['GET', 'POST'])
@login_required
def add_inventory_item():

    if request.method == 'POST':
        seller_id = current_user.id
        product_name = request.form.get('product_name')
        product_price = request.form.get('product_price', type=float)
        product_quantity = request.form.get('product_quantity', type=int)

        InventoryItems.add_inventory_item(seller_id, product_name, product_price, product_quantity)
        flash("New product added to inventory successfully.", "success")
        return redirect(url_for('inventory.view_inventory'))

    return render_template('add_inventory_item.html') """

@bp.route('/add_new_product', methods=['GET', 'POST'])
@login_required
def add_new_product():
    """
    Adds a new product to the seller's inventory.
    """
    if request.method == 'POST':
        seller_id = current_user.id
        product_name = request.form.get('product_name')
        product_price = request.form.get('product_price', type=float)
        product_quantity = request.form.get('product_quantity', type=int)

        # Add the new product to the Products table using the helper function
        InventoryItems.add_new_product(seller_id, product_name, product_price, product_quantity)

        flash("New product added successfully.", "success")
        return redirect(url_for('inventory.view_inventory'))

    return render_template('add_new_product.html')


@bp.route('/orders_dashboard')
@login_required
def orders_dashboard():
    seller_id = current_user.id

    # Separate page numbers for unfulfilled and fulfilled orders
    unfulfilled_page = request.args.get('unfulfilled_page', default=1, type=int)
    fulfilled_page = request.args.get('fulfilled_page', default=1, type=int)
    per_page = 5

    # Get paginated unfulfilled and fulfilled orders separately BASED on seller-specific status
    unfulfilled_orders, total_unfulfilled = Order.get_paginated_seller_orders(
        seller_id, ['Incomplete'], unfulfilled_page, per_page
    )
    fulfilled_orders, total_fulfilled = Order.get_paginated_seller_orders(
        seller_id, ['Fulfilled'], fulfilled_page, per_page
    )

    total_unfulfilled_pages = (total_unfulfilled + per_page - 1) // per_page
    total_fulfilled_pages = (total_fulfilled + per_page - 1) // per_page

    return render_template(
        'orders_dashboard.html',
        unfulfilled_orders=unfulfilled_orders,
        fulfilled_orders=fulfilled_orders,
        unfulfilled_page=unfulfilled_page,
        total_unfulfilled_pages=total_unfulfilled_pages,
        fulfilled_page=fulfilled_page,
        total_fulfilled_pages=total_fulfilled_pages,
    )


@bp.route('/order_dashboard_details/<int:order_id>')
@login_required
def order_dashboard_details(order_id):
    seller_id = current_user.id

    # Get the updated order metadata
    order = Order.get_order_by_seller(seller_id, order_id)
    if not order:
        flash("Order not found or you don't have products in this order.", "error")
        return redirect(url_for('inventory.orders_dashboard'))

    # Get the paginated details of items sold by the seller
    page = request.args.get('page', default=1, type=int)
    per_page = 100
    order_items, total_items = Order.get_order_details_for_seller(seller_id, order_id, page, per_page)

    # Get the buyer address using the helper function
    buyer_address = Order.get_user_address_by_order(order_id)

    return render_template(
        'order_dashboard_details.html',
        order=order,
        order_items=order_items,
        total_items=total_items,
        buyer_address=buyer_address,
        overall_fulfillment_status=order.fulfillment_status  # Ensure it's the updated status
    )


@bp.route('/update_item_fulfillment_status', methods=['POST'])
@login_required
def update_item_fulfillment_status():
    order_id = request.form.get('order_id', type=int)
    product_id = request.form.get('product_id', type=int)
    new_status = request.form.get('new_status')

    # Validate that the new status is acceptable
    allowed_statuses = ['Incomplete', 'Fulfilled']
    if new_status not in allowed_statuses:
        flash("Invalid fulfillment status.", "error")
        return redirect(url_for('inventory.order_dashboard_details', order_id=order_id))

    Order.update_item_fulfillment_status(order_id, product_id, new_status)
    
    flash(f"Item status updated successfully to {new_status}.", "success")
    return redirect(url_for('inventory.order_dashboard_details', order_id=order_id))

