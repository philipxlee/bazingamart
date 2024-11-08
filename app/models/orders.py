from flask import current_app
from app.models.helpers.db_exceptions_wrapper import handle_db_exceptions

class Order:
    """
    This class represents a user's completed order. It provides methods to retrieve
    order summaries and detailed order information.
    """

    def __init__(self, order_id, total_price, created_at, coupon_code=None):
        self.order_id = order_id
        self.total_price = total_price
        self.created_at = created_at
        self.coupon_code = coupon_code

    @staticmethod
    @handle_db_exceptions
    def get_all_orders(user_id) -> list:
        """
        Retrieves all completed orders for a given user.
        @param user_id: The user ID to get the orders for.
        """
        rows = current_app.db.execute(
            """
            SELECT order_id, total_price, created_at, coupon_code
            FROM Orders
            WHERE user_id = :user_id
            ORDER BY created_at DESC
            """,
            user_id=user_id
        )
        return [Order(row[0], row[1], row[2], row[3]) for row in rows]

    @staticmethod
    @handle_db_exceptions
    def get_order_details(order_id) -> list:
        """
        Retrieves the specific order details for a given order ID.
        In other words, this method returns a submitted cart.
        @param order_id: The order ID to get the details for.
        """
        rows = current_app.db.execute(
            """
            SELECT p.name, cp.quantity, cp.unit_price
            FROM CartProducts cp
            JOIN Products p ON cp.product_id = p.id
            WHERE cp.order_id = :order_id
            """,
            order_id=order_id
        )
        return rows