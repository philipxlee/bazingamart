from flask import Blueprint, render_template, request, flash, current_app
from flask_login import login_required, current_user
import datetime
from .models.product import Product
from app.models.helpers.db_exceptions_wrapper import handle_db_exceptions

bp = Blueprint('index', __name__)

@bp.route('/')
def index():
    # Get the current page and items per page for pagination
    page = request.args.get('page', 1, type=int)
    items_per_page = 9

    # Get the filter and sort parameters from the request
    search = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip()
    sort = request.args.get('sort', '').strip()

    # Base query with average rating and review count calculation
    query = """
    SELECT p.product_id, p.product_name, p.price, p.available, 
           p.seller_id, p.product_quantity, p.description, 
           p.image, p.category, 
           COALESCE(ROUND(AVG(r.stars), 1), 0) AS average_rating,
           COUNT(r.review_id) AS num_reviews
    FROM Products p
    LEFT JOIN Reviews r ON p.product_id = r.product_id
    WHERE p.available = TRUE
    """
    params = {}

    # Apply search filter
    if search:
        query += """
            AND (p.product_name ILIKE :search OR p.description ILIKE :search)
        """
        params['search'] = f"%{search}%"

    # Apply category filter
    if category:
        query += " AND p.category = :category"
        params['category'] = category

    # Group by product ID to calculate average rating and review count
    query += """
        GROUP BY p.product_id, p.product_name, p.price, p.available, 
                 p.seller_id, p.product_quantity, p.description, 
                 p.image, p.category
    """

    # Apply sorting by price
    if sort == 'asc':
        query += " ORDER BY p.price ASC"
    elif sort == 'desc':
        query += " ORDER BY p.price DESC"
    
    # Calculate the offset for pagination
    offset = (page - 1) * items_per_page
    query += " LIMIT :limit OFFSET :offset"
    params['limit'] = items_per_page
    params['offset'] = offset

    # Execute the query to get filtered products
    filtered_products = current_app.db.execute(query, **params)

    # Get the total count of products for calculating total pages
    count_query = """
        SELECT COUNT(*) FROM Products p
        WHERE p.available = TRUE
    """
    count_params = {}  # Use a separate params dictionary for count query
    if search:
        count_query += """
            AND (p.product_name ILIKE :search OR p.description ILIKE :search)
        """
        count_params['search'] = f"%{search}%"
    if category:
        count_query += " AND p.category = :category"
        count_params['category'] = category

    total_items_result = current_app.db.execute(count_query, **count_params)
    total_items = total_items_result[0][0]  # Extract count from the result
    total_pages = (total_items + items_per_page - 1) // items_per_page

    # Get distinct categories for the dropdown in the UI
    categories = current_app.db.execute(
        "SELECT DISTINCT category FROM Products WHERE available = TRUE"
    )

    # Render the page with the filtered product items
    return render_template(
        'index.html',
        product_items=filtered_products,
        categories=[c[0] for c in categories],
        page=page,
        total_pages=total_pages
    )


