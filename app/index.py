from flask import render_template, request
from flask_login import current_user
import datetime

from .models.product import Product

from flask import Blueprint
bp = Blueprint('index', __name__)


@bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 9
    products, total_pages = Product.get_all(available=True, page=page, per_page=per_page)
    return render_template('index.html',
                           avail_products=products,
                           page=page,
                           total_pages=total_pages)