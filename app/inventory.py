from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from app.models.inventory_items import InventoryItems

bp = Blueprint('inventory', __name__)

@bp.route('/view_inventory')
@login_required
def view_inventory():
    seller_id = current_user.id
    inventory_items = InventoryItems.get_all_by_user(seller_id)
    return render_template('view_inventory_page.html', inventory_items=inventory_items)