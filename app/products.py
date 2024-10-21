from flask import render_template
from flask_login import current_user
from flask import request

import datetime

from .models.product import Product
from .models.purchase import Purchase

from flask import Blueprint
bp = Blueprint('products', __name__)


@bp.route('/search_by_price', methods=['GET', 'POST'])
def search_by_price():
    if request.method == 'POST':
        k = int(request.form['k_value'])  # Get the value entered by the user
        top_products = Product.get_top_k_expensive(k)
        return render_template('search_by_price.html',
                               avail_products=Product.get_all(True),
                               top_products=top_products)
    return render_template('search_by_price.html')