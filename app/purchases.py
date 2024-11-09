from flask import Blueprint, render_template, current_app
from flask_login import login_required, current_user
from app.models.purchase import Purchase


bp = Blueprint('purchases', __name__)

@bp.route('/recent_purchases')
@login_required
def recent_purchases():
    purchases = current_app.db.execute(
        """
        SELECT p.id, pr.name, p.quantity, p.price, (p.quantity * p.price) AS total_spent, p.time_purchased
        FROM Purchases p
        JOIN Products pr ON p.pid = pr.id
        WHERE p.uid = :user_id
        ORDER BY p.time_purchased DESC
        """,
        user_id=current_user.id
    )
    return render_template('recent_purchases.html', purchase_history=purchases)