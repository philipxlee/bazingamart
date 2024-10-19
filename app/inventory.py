from flask import Blueprint, render_template
from flask_login import login_required, current_user
from app.models.inventory_items import InventoryItems

bp = Blueprint('inventory', __name__)

@bp.route('/view_inventory')
@login_required
def view_inventory():
    # Get the current seller's ID from the logged-in user
    seller_id = current_user.id
    # Fetch all inventory items for this seller
    inventory_items = InventoryItems.get_all_items(seller_id)
    # Render the template and pass the inventory items
    return render_template('view_inventory_page.html', inventory_items=inventory_items)
