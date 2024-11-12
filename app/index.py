from flask import Blueprint, render_template, request, flash, current_app
from flask_login import login_required, current_user
import datetime
from .models.product import Product
from app.models.helpers.db_exceptions_wrapper import handle_db_exceptions


bp = Blueprint('index', __name__)


@bp.route('/')
def index():

    page = request.args.get('page', 1, type=int)
    items_per_page = 9
    # get all available products for sale:
    products = Product.get_all(True)

    # Use the helper method to retrieve paginated inventory items for the seller
    product_items = Product.get_all_paginated(page, items_per_page, True)
    total_items = Product.get_count_products(True)
    total_pages = (total_items + items_per_page - 1) // items_per_page

    # render the page by adding information to the index.html file
    return render_template('index.html',
                           product_items=product_items, page=page, total_pages=total_pages)




# @bp.route('/')
# def index():
#     page = request.args.get('page', 1, type=int)
#     items_per_page = 9

#     # Use the helper method to retrieve paginated product items
#     product_items = Product.get_all_paginated(page, items_per_page, True)
#     total_items = Product.get_count_products(True)
#     total_pages = (total_items + items_per_page - 1) // items_per_page

#     # Render the page by adding information to the index.html file
#     return render_template('index.html',
#                            product_items=product_items,
#                            page=page,
#                            total_pages=total_pages)