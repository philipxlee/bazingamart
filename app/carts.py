from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint('carts', __name__)

@bp.route('/view_cart')
@login_required
def view_cart():
    return render_template('view_carts_page.html')