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
    def get_all_orders(user_id, page=1, per_page=5) -> list:
        """
        Retrieves paginated orders for a given user.
        """
        offset = (page - 1) * per_page
        sql = """
            SELECT order_id, total_price, created_at, coupon_code
            FROM Orders
            WHERE user_id = :user_id
            ORDER BY created_at DESC
            LIMIT :per_page OFFSET :offset
            """
        rows = current_app.db.execute(
            sql,
            user_id=user_id,
            per_page=per_page,
            offset=offset
        )
        return [Order(row[0], row[1], row[2], row[3]) for row in rows]

    @staticmethod
    @handle_db_exceptions
    def count_orders(user_id) -> int:
        """
        Counts the total number of orders for a given user.
        """
        result = current_app.db.execute(
            """
            SELECT COUNT(*) FROM Orders WHERE user_id = :user_id
            """,
            user_id=user_id
        )
        return result[0][0] if result else 0

    @staticmethod
    @handle_db_exceptions
    def get_order(user_id, order_id) -> 'Order':
        """
        Retrieves a specific order for a given user and order ID.
        @param user_id: The ID of the user.
        @param order_id: The ID of the order to retrieve.
        @return: An Order object if found, else None.
        """
        rows = current_app.db.execute(
            """
            SELECT order_id, total_price, created_at, coupon_code
            FROM Orders
            WHERE user_id = :user_id AND order_id = :order_id
            """,
            user_id=user_id,
            order_id=order_id
        )
        if rows:
            row = rows[0]
            return Order(row[0], row[1], row[2], row[3])
        else:
            return None

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
            SELECT p.product_name, cp.quantity, cp.unit_price
            FROM CartProducts cp
            JOIN Products p ON cp.product_id = p.product_id
            WHERE cp.order_id = :order_id
            """,
            order_id=order_id
        )
        return rows
