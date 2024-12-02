from flask import Blueprint, render_template, request, flash, current_app
from flask_login import login_required, current_user
import datetime
from .models.product import Product
from app.models.helpers.db_exceptions_wrapper import handle_db_exceptions


bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    # Get the filter and sort parameters from the request
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    sort = request.args.get('sort', '').strip()

    # Start with base query for products that are available
    query = """
        SELECT * FROM Products
        WHERE available = TRUE
    """
    params = {}

    # Apply search filter
    if search:
        query += """
            AND (product_name ILIKE :search OR description ILIKE :search)
        """
        params['search'] = f"%{search}%"

    # Apply category filter
    if category:
        query += " AND category = :category"
        params['category'] = category

    # Apply sorting by price
    if sort == 'asc':
        query += " ORDER BY price ASC"
    elif sort == 'desc':
        query += " ORDER BY price DESC"

    # Execute the query
    filtered_products = current_app.db.execute(query, **params)

    # Get distinct categories for the dropdown in the UI
    categories = current_app.db.execute(
        "SELECT DISTINCT category FROM Products WHERE available = TRUE"
    )

    # Render the page with the filtered product items
    return render_template(
        'index.html',
        product_items=filtered_products,
        categories=[c[0] for c in categories],
        page=1,  # Temporary placeholder value
        total_pages=1  # Temporary placeholder value
    )


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
