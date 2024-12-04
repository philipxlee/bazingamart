from flask import render_template, request, Blueprint
from flask_login import current_user
from .models.product import Product
from .models.inventory_items import InventoryItems 
from .models.reviews import Reviews  
import datetime

bp = Blueprint('products', __name__)

@bp.route('/product/<int:product_id>', methods=['GET'])
def product_detail(product_id):
    product = Product.get(product_id)    # Fetch product details
    sellers = InventoryItems.get_all_by_product(product_id)   # Fetch sellers for this product
    reviews = Reviews.get_reviews_by_product(product_id)  # Fetch reviews for this product

    return render_template(
        'product_detail.html',
        product=product,
        sellers=sellers,
        reviews=reviews
    )




@bp.route('/product/<int:product_id>/seller/<int:seller_id>', methods=['GET'])
def seller_detail(product_id, seller_id):
    
    # Fetch product details
    product = Product.get(product_id)

    # Fetch the selected seller's inventory details
    seller_info = InventoryItems.get_detailed_inventory_item(seller_id, product_id)

    print(f"Seller info fetched: {seller_info.__dict__ if seller_info else 'None'}")


    # Fetch all sellers for the dropdown, to show alternative sellers for this product
    sellers = InventoryItems.get_all_by_product(product_id)

    # Fetch reviews specific to this seller (use real logic when reviews are ready)
    #reviews = Reviews.get_reviews_by_seller(product_id, seller_id) if hasattr(Reviews, 'get_reviews_by_seller') else []

    return render_template(
        'product_detail.html',
        product=product,
        sellers=sellers,
        seller=seller_info,
        seller_id=seller_id,
        #reviews=reviews
    )

@bp.route('/search_by_price', methods=['GET', 'POST'])
def search_by_price():
    if request.method == 'POST':
        k = int(request.form['k_value'])  # Get the value entered by the user
        top_products = Product.get_top_k_expensive(k)
        return render_template('search_by_price.html',
                               avail_products=Product.get_all(True),
                               top_products=top_products)
    return render_template('search_by_price.html')