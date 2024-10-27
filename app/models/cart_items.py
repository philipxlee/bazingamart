from flask import current_app
from app.models.helpers.db_exceptions_wrapper import handle_db_exceptions


class CartItems:
    """
    This class represents all the items within a user's cart. It provides API services
    to add, remove, and update item quantities from the cart. Additionally, it provides
    methods to view the items and calculate the total cost of all items in the cart.
    """

    def __init__(self, product_id, order_id, quantity, unit_price):
        self.product_id = product_id
        self.order_id = order_id
        self.quantity = quantity
        self.unit_price = unit_price

    @staticmethod
    def get_all_items(user_id) -> list:
        """
        Returns all items in the cart for the given user.
        @param user_id: The user ID to get the cart items for.
        """
        rows = current_app.db.execute(
            """
            SELECT cp.product_id, cp.order_id, cp.quantity, cp.unit_price
            FROM CartProducts cp
            JOIN Cart c ON cp.order_id = c.order_id
            WHERE c.user_id = :user_id AND c.purchase_status = 'Pending'
            """,
            user_id=user_id,
        )

        items_in_cart = [CartItems(*row) for row in rows]
        return items_in_cart

    @staticmethod
    @handle_db_exceptions
    def add_item(user_id, product_id, quantity):
        """
        Adds an item to the cart after checking inventory.
        @param user_id: The user ID to add the item for.
        @param product_id: The product ID to add to the cart.
        @param quantity: The quantity of the product to add.
        """

        # 1. Check inventory
        available_quantity = CartItems._get_available_inventory(product_id)
        if available_quantity is None:
            return "Product not found in inventory."
        if quantity > available_quantity:
            return "Not enough inventory available."

        # 2. Get unit price of the product
        unit_price = CartItems._get_product_price(product_id)
        if unit_price is None:
            return "Product not found."

        # 3. Validation for if the product is already in the cart
        order_id = CartItems._get_or_create_pending_cart(user_id)
        existing_item = CartItems._get_existing_cart_item(order_id, product_id)
        
        if existing_item:
            new_quantity = existing_item[0][0] + quantity
            if new_quantity > available_quantity:
                return "Not enough inventory available for the requested quantity."
            CartItems._update_cart_item(order_id, product_id, new_quantity)
        else:
            CartItems._insert_cart_item(order_id, product_id, quantity, unit_price)

        return "success"

    @staticmethod
    @handle_db_exceptions
    def remove_item(user_id, product_id):
        """
        Removes an item from the cart.
        @param user_id: The user ID to remove the item for.
        @param product_id: The product ID to remove from the cart.
        """
        order_id = CartItems._get_pending_cart_id(user_id)
        if order_id is None:
            return "No pending cart found."

        CartItems._delete_cart_item(order_id, product_id)
        return "success"

    @staticmethod
    @handle_db_exceptions
    def update_item_quantity(user_id, product_id, new_quantity):
        """
        Updates the quantity of an item in the cart.
        @param user_id: The user ID to update the item for.
        @param product_id: The product ID to update the quantity for.
        @param new_quantity: The new quantity of the product.
        """
        order_id = CartItems._get_pending_cart_id(user_id)
        if not order_id:
            return "No pending cart found."

        if new_quantity <= 0:
            return CartItems.remove_item(user_id, product_id)

        if not CartItems._is_valid_quantity(product_id, new_quantity):
            return "Not enough inventory available."

        CartItems._update_cart_item(order_id, product_id, new_quantity)
        return "success"

    @staticmethod
    def _get_available_inventory(product_id):
        inventory_row = current_app.db.execute(
            """
            SELECT product_quantity FROM Inventory
            WHERE product_id = :product_id
            """,
            product_id=product_id,
        )
        return inventory_row[0][0] if inventory_row else None

    @staticmethod
    def _get_or_create_pending_cart(user_id):
        rows = current_app.db.execute(
            """
            SELECT order_id FROM Cart
            WHERE user_id = :user_id AND purchase_status = 'Pending'
            """,
            user_id=user_id,
        )
        if rows:
            return rows[0][0]
        else:
            new_cart = current_app.db.execute(
                """
                INSERT INTO Cart (user_id, total_price, purchase_status)
                VALUES (:user_id, 0.0, 'Pending')
                RETURNING order_id
                """,
                user_id=user_id,
            )
            return new_cart[0][0]

    @staticmethod
    def _get_product_price(product_id):
        price_row = current_app.db.execute(
            """
            SELECT price FROM Products WHERE id = :product_id
            """,
            product_id=product_id,
        )
        return price_row[0][0] if price_row else None

    @staticmethod
    def _get_existing_cart_item(order_id, product_id):
        existing_item = current_app.db.execute(
            """
            SELECT quantity FROM CartProducts
            WHERE order_id = :order_id AND product_id = :product_id
            """,
            order_id=order_id,
            product_id=product_id,
        )
        return existing_item

    @staticmethod
    def _update_cart_item(order_id, product_id, new_quantity):
        current_app.db.execute(
            """
            UPDATE CartProducts
            SET quantity = :new_quantity
            WHERE order_id = :order_id AND product_id = :product_id
            """,
            order_id=order_id,
            product_id=product_id,
            new_quantity=new_quantity,
        )

    @staticmethod
    def _insert_cart_item(order_id, product_id, quantity, unit_price):
        current_app.db.execute(
            """
            INSERT INTO CartProducts (order_id, product_id, quantity, unit_price)
            VALUES (:order_id, :product_id, :quantity, :unit_price)
            """,
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price,
        )

    @staticmethod
    def _get_pending_cart_id(user_id):
        order_id_row = current_app.db.execute(
            """
            SELECT order_id FROM Cart
            WHERE user_id = :user_id AND purchase_status = 'Pending'
            """,
            user_id=user_id,
        )
        return order_id_row[0][0] if order_id_row else None

    @staticmethod
    def _delete_cart_item(order_id, product_id):
        current_app.db.execute(
            """
            DELETE FROM CartProducts
            WHERE order_id = :order_id AND product_id = :product_id
            """,
            order_id=order_id,
            product_id=product_id,
        )

    @staticmethod
    def _is_valid_quantity(product_id, requested_quantity):
        available_quantity = CartItems._get_available_inventory(product_id)
        return (
            available_quantity is not None and requested_quantity <= available_quantity
        )
