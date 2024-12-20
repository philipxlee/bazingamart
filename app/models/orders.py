from flask import current_app
from app.models.helpers.db_exceptions_wrapper import handle_db_exceptions
from app.models.user import User


class Order:
    """
    This class represents a user's completed order. It provides methods to retrieve
    order summaries and detailed order information.
    """

    def __init__(
        self,
        order_id,
        total_price,
        created_at,
        coupon_code=None,
        fulfillment_status="Incomplete",
    ):
        self.order_id = order_id
        self.total_price = total_price
        self.created_at = created_at
        self.coupon_code = coupon_code
        self.fulfillment_status = fulfillment_status

    @staticmethod
    @handle_db_exceptions
    def get_all_orders(user_id, page=1, per_page=5) -> list:
        """
        Retrieves paginated orders for a given user, including seller IDs.
        """
        offset = (page - 1) * per_page
        sql = """
            SELECT 
                o.order_id, 
                o.total_price, 
                o.created_at, 
                o.coupon_code, 
                o.fulfillment_status,
                STRING_AGG(DISTINCT CAST(cp.seller_id AS TEXT), ', ') AS seller_ids
            FROM Orders o
            JOIN CartProducts cp ON o.order_id = cp.order_id
            WHERE o.user_id = :user_id
            GROUP BY o.order_id, o.total_price, o.created_at, o.coupon_code, o.fulfillment_status
            ORDER BY o.created_at DESC
            LIMIT :per_page OFFSET :offset
        """
        rows = current_app.db.execute(
            sql, user_id=user_id, per_page=per_page, offset=offset
        )
        return [
            {
                "order_id": row[0],
                "total_price": row[1],
                "created_at": row[2],
                "coupon_code": row[3],
                "fulfillment_status": row[4],
                "seller_ids": row[5]  # List of seller IDs
            }
            for row in rows
        ]

    @staticmethod
    @handle_db_exceptions
    def count_orders(user_id) -> int:
        """Counts the total number of orders for a given user."""
        result = current_app.db.execute(
            """
            SELECT COUNT(*) FROM Orders WHERE user_id = :user_id
            """,
            user_id=user_id,
        )
        return result[0][0] if result else 0

    @staticmethod
    @handle_db_exceptions
    def get_order(user_id, order_id) -> "Order":
        """
        Retrieves a specific order for a given user and order ID.
        @param user_id: The ID of the user.
        @param order_id: The ID of the order to retrieve.
        @return: An Order object if found, else None.
        """
        rows = current_app.db.execute(
            """
            SELECT order_id, total_price, created_at, coupon_code, fulfillment_status
            FROM Orders
            WHERE user_id = :user_id AND order_id = :order_id
            """,
            user_id=user_id,
            order_id=order_id,
        )
        if rows:
            row = rows[0]
            return Order(row[0], row[1], row[2], row[3], row[4])
        else:
            return None

    @staticmethod
    @handle_db_exceptions
    def get_order_details(order_id, page=1, per_page=100):
        """
        Retrieves details of an order given the order ID
        """
        offset = (page - 1) * per_page
        rows = current_app.db.execute(
            """
            SELECT p.product_name, cp.quantity, cp.unit_price, cp.product_id, cp.fulfillment_status, cp.seller_id
            FROM CartProducts cp
            JOIN Products p ON cp.product_id = p.product_id AND cp.seller_id = p.seller_id
            WHERE cp.order_id = :order_id
            LIMIT :per_page OFFSET :offset
            """,
            order_id=order_id,
            per_page=per_page,
            offset=offset,
        )

        total_items = current_app.db.execute(
            """
            SELECT COUNT(*)
            FROM CartProducts
            WHERE order_id = :order_id
            """,
            order_id=order_id,
        )[0][0]

        order_items = []
        for row in rows:
            (
                product_name,
                quantity,
                unit_price,
                product_id,
                fulfillment_status,
                seller_id,
            ) = row
            order_items.append(
                {
                    "product_name": product_name,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "product_id": product_id,
                    "fulfillment_status": fulfillment_status,
                    "seller_id": seller_id,
                }
            )

        return order_items, total_items


    @staticmethod
    @handle_db_exceptions
    def get_seller_orders(seller_id, page=1, per_page=5):
        """
        Retrieves paginated lists of orders involving products sold by the seller.
        Returns two lists: unfulfilled_orders and fulfilled_orders.
        """
        offset = (page - 1) * per_page

        # Retrieve unfulfilled orders
        unfulfilled_rows = current_app.db.execute(
            """
            SELECT 
                o.order_id,
                o.created_at,
                SUM(cp.quantity * cp.unit_price) AS total_price,
                o.fulfillment_status
            FROM Orders o
            JOIN CartProducts cp ON o.order_id = cp.order_id
            WHERE cp.seller_id = :seller_id 
            AND o.fulfillment_status IN ('Incomplete')
            GROUP BY o.order_id, o.created_at, o.fulfillment_status
            ORDER BY o.created_at DESC
            LIMIT :per_page OFFSET :offset
        """,
            seller_id=seller_id,
            per_page=per_page,
            offset=offset,
        )

        # Retrieve fulfilled orders
        fulfilled_rows = current_app.db.execute(
            """
            SELECT 
                o.order_id,
                o.created_at,
                SUM(cp.quantity * cp.unit_price) AS total_price,
                o.fulfillment_status
            FROM Orders o
            JOIN CartProducts cp ON o.order_id = cp.order_id
            WHERE cp.seller_id = :seller_id 
            AND o.fulfillment_status IN ('Fulfilled', 'Shipped', 'Delivered')
            GROUP BY o.order_id, o.created_at, o.fulfillment_status
            ORDER BY o.created_at DESC
            LIMIT :per_page OFFSET :offset
            """,
            seller_id=seller_id,
            per_page=per_page,
            offset=offset,
        )

        unfulfilled_orders = [
            {
                "order_id": row[0],
                "created_at": row[1],
                "total_price": row[2],
                "fulfillment_status": row[3],
            }
            for row in unfulfilled_rows
        ]
        fulfilled_orders = [
            {
                "order_id": row[0],
                "created_at": row[1],
                "total_price": row[2],
                "fulfillment_status": row[3],
            }
            for row in fulfilled_rows
        ]

        return unfulfilled_orders, fulfilled_orders

    @staticmethod
    @handle_db_exceptions
    def get_paginated_seller_orders(seller_id, statuses, page, per_page):
        """
        Retrieves paginated lists of orders involving products sold by the seller.
        """
        offset = (page - 1) * per_page

        # Prepare statuses for SQL query
        if isinstance(statuses, list):
            status_placeholder = ",".join(f"'{s}'" for s in statuses)
        else:
            status_placeholder = f"'{statuses}'"

        sql = f"""
            SELECT 
                o.order_id,
                o.created_at,
                SUM(cp.quantity * cp.unit_price) AS total_price,
                CASE 
                    WHEN COUNT(*) = SUM(CASE WHEN cp.fulfillment_status = 'Fulfilled' THEN 1 ELSE 0 END) 
                    THEN 'Fulfilled' 
                    ELSE 'Incomplete' 
                END AS seller_fulfillment_status
            FROM Orders o
            JOIN CartProducts cp ON o.order_id = cp.order_id
            WHERE cp.seller_id = :seller_id
            GROUP BY o.order_id, o.created_at
            HAVING CASE 
                        WHEN COUNT(*) = SUM(CASE WHEN cp.fulfillment_status = 'Fulfilled' THEN 1 ELSE 0 END) 
                        THEN 'Fulfilled' 
                        ELSE 'Incomplete' 
                END IN ({status_placeholder})
            ORDER BY o.created_at DESC
            LIMIT :per_page OFFSET :offset
        """

        rows = current_app.db.execute(
            sql, seller_id=seller_id, per_page=per_page, offset=offset
        )

        total_items = current_app.db.execute(
            f"""
            SELECT COUNT(*)
            FROM (
                SELECT 
                    o.order_id
                FROM Orders o
                JOIN CartProducts cp ON o.order_id = cp.order_id
                WHERE cp.seller_id = :seller_id
                GROUP BY o.order_id
                HAVING CASE 
                            WHEN COUNT(*) = SUM(CASE WHEN cp.fulfillment_status = 'Fulfilled' THEN 1 ELSE 0 END) 
                            THEN 'Fulfilled' 
                            ELSE 'Incomplete' 
                    END IN ({status_placeholder})
            ) AS subquery
            """,
            seller_id=seller_id,
        )[0][0]

        orders = [
            {
                "order_id": row[0],
                "created_at": row[1],
                "total_price": row[2],
                "fulfillment_status": row[3], 
            }
            for row in rows
        ]
        return orders, total_items


    @staticmethod
    @handle_db_exceptions
    def get_order_by_seller(seller_id, order_id) -> "Order":
        """
        Retrieves orders involving products sold by the seller.
        """
        rows = current_app.db.execute(
            """
            SELECT 
                o.order_id, 
                SUM(cp.quantity * cp.unit_price) AS total_price, 
                o.created_at, 
                o.coupon_code, 
                CASE 
                    WHEN COUNT(*) = SUM(CASE WHEN cp.fulfillment_status = 'Fulfilled' THEN 1 ELSE 0 END) 
                    THEN 'Fulfilled' 
                    ELSE 'Incomplete' 
                END AS seller_fulfillment_status
            FROM Orders o
            JOIN CartProducts cp ON o.order_id = cp.order_id
            WHERE cp.seller_id = :seller_id AND o.order_id = :order_id
            GROUP BY o.order_id, o.created_at, o.coupon_code
            """,
            seller_id=seller_id,
            order_id=order_id,
        )

        if rows:
            row = rows[0]
            return Order(row[0], row[1], row[2], row[3], fulfillment_status=row[4])
        else:
            return None


    @staticmethod
    @handle_db_exceptions
    def get_order_details_for_seller(seller_id, order_id, page, per_page):
        """
        Retrieves order details given a seller ID and order ID
        """
        offset = (page - 1) * per_page
        rows = current_app.db.execute(
            """
            SELECT p.product_name, cp.quantity, cp.unit_price, cp.product_id, cp.fulfillment_status
            FROM CartProducts cp
            JOIN Products p ON cp.product_id = p.product_id AND cp.seller_id = p.seller_id
            WHERE cp.seller_id = :seller_id AND cp.order_id = :order_id
            LIMIT :per_page OFFSET :offset
            """,
            seller_id=seller_id,
            order_id=order_id,
            per_page=per_page,
            offset=offset,
        )

        total_items = current_app.db.execute(
            """
            SELECT COUNT(*)
            FROM CartProducts
            WHERE seller_id = :seller_id AND order_id = :order_id
            """,
            seller_id=seller_id,
            order_id=order_id,
        )[0][0]

        order_items = []
        for row in rows:
            product_name, quantity, unit_price, product_id, fulfillment_status = row
            order_items.append(
                {
                    "product_name": product_name,
                    "quantity": quantity,
                    "unit_price": unit_price,
                    "product_id": product_id,
                    "fulfillment_status": fulfillment_status,
                }
            )

        return order_items, total_items


    @staticmethod
    @handle_db_exceptions
    def get_user_address_by_order(order_id):
        """Retrieves the user's address based on the given order ID."""
        # Fetch the user_id from the Orders table based on the order_id
        rows = current_app.db.execute(
            """
            SELECT user_id
            FROM Orders
            WHERE order_id = :order_id
            """,
            order_id=order_id,
        )

        if rows:
            user_id = rows[0][0]
            # Use User class method to fetch the address
            return User.get_address(user_id)
        return None

    @staticmethod
    @handle_db_exceptions
    def update_item_fulfillment_status(order_id, product_id, seller_id, new_status):
        """
        Updates the fulfillment status of an individual item in the order and 
        recalculates the overall order fulfillment status.
        Ensures the database is updated and changes are committed.
        """
        # Define allowed statuses
        allowed_statuses = ["Incomplete", "Fulfilled"]
        if new_status not in allowed_statuses:
            raise ValueError("Invalid fulfillment status. Must be 'Incomplete' or 'Fulfilled'.")

        # Update the fulfillment status of the specific item
        rows_affected = current_app.db.execute(
            """
            UPDATE CartProducts
            SET fulfillment_status = :new_status
            WHERE order_id = :order_id AND product_id = :product_id AND seller_id = :seller_id
            """,
            order_id=order_id,
            product_id=product_id,
            seller_id=seller_id,
            new_status=new_status,
        )

        # Check if any row was updated
        if rows_affected == 0:
            raise ValueError(f"No matching item found for Order ID: {order_id}, Product ID: {product_id}, Seller ID: {seller_id}.")

        # Commit the changes to ensure persistence
        current_app.db.commit()

        # Recalculate the overall order fulfillment status
        Order.recalculate_order_fulfillment_status(order_id)




    @staticmethod
    @handle_db_exceptions
    def recalculate_order_fulfillment_status(order_id):
        """
        Recalculates the overall fulfillment status of an order by checking the statuses
        of all items in the order and updating the database accordingly.
        """
        # Fetch all item statuses for the order
        item_statuses = current_app.db.execute(
            """
            SELECT fulfillment_status
            FROM CartProducts
            WHERE order_id = :order_id
            """,
            order_id=order_id,
        )

        # Extract the statuses into a list
        item_statuses = [row[0] for row in item_statuses]

        # Determine the overall status:
        # - 'Fulfilled' if all items are fulfilled
        # - 'Incomplete' otherwise
        overall_status = "Fulfilled" if all(status == "Fulfilled" for status in item_statuses) else "Incomplete"

        # Update the overall order status in the database
        current_app.db.execute(
            """
            UPDATE Orders
            SET fulfillment_status = :overall_status
            WHERE order_id = :order_id
            """,
            order_id=order_id,
            overall_status=overall_status,
        )

        # Commit the changes to ensure the update is persisted
        current_app.db.commit()

