from flask import current_app
from app.models.helpers.db_exceptions_wrapper import handle_db_exceptions
from app.models.coupons import Coupons

from flask import current_app
from app.models.helpers.db_exceptions_wrapper import handle_db_exceptions
from app.models.coupons import Coupons


class CartItems:
    """
    This class represents all the items within a user's cart. It provides API services
    to add, remove, and update item quantities from the cart. Additionally, it provides
    methods to view the items and calculate the total cost of all items in the cart.
    to add, remove, and update item quantities from the cart. Additionally, it provides
    methods to view the items and calculate the total cost of all items in the cart.
    """

    def __init__(self, product_id, seller_id, order_id, quantity, unit_price, product_name):
        self.product_id = product_id
        self.seller_id = seller_id
        self.order_id = order_id
        self.quantity = quantity
        self.unit_price = unit_price
        self.product_name = product_name

    @staticmethod
    def get_all_cart_items(user_id) -> list:
        """
        Returns all items in the cart for the given user, including product name.
        @param user_id: The user ID to get the cart items for.
        """
        rows = current_app.db.execute(
            """
            SELECT cp.product_id, cp.seller_id, cp.order_id, cp.quantity, cp.unit_price, p.product_name
            FROM CartProducts cp
            JOIN Cart c ON cp.order_id = c.order_id
            JOIN Products p ON cp.product_id = p.product_id AND cp.seller_id = p.seller_id
            WHERE c.user_id = :user_id AND c.purchase_status = 'Pending'
            """,
            user_id=user_id,
        )
        items_in_cart = [CartItems(row[0], row[1], row[2], row[3], row[4], row[5]) for row in rows]
        return items_in_cart

    @staticmethod
    def get_all_items(user_id, page=1, per_page=5) -> tuple:
        """
        Returns paginated items in the cart for the given user, including product name.
        @param user_id: The user ID to get the cart items for.
        @param page: The current page number for pagination.
        @param per_page: The number of items per page.
        @return: A tuple of (items_in_cart, total_items).
        """
        offset = (page - 1) * per_page
        rows = current_app.db.execute(
            """
            SELECT cp.product_id, cp.seller_id, cp.order_id, cp.quantity, cp.unit_price, p.product_name
            FROM CartProducts cp
            JOIN Cart c ON cp.order_id = c.order_id
            JOIN Products p ON cp.product_id = p.product_id AND cp.seller_id = p.seller_id
            WHERE c.user_id = :user_id AND c.purchase_status = 'Pending'
            LIMIT :per_page OFFSET :offset
            """,
            user_id=user_id,
            per_page=per_page,
            offset=offset,
        )
        total_items = current_app.db.execute(
            """
            SELECT COUNT(*)
            FROM CartProducts cp
            JOIN Cart c ON cp.order_id = c.order_id
            WHERE c.user_id = :user_id AND c.purchase_status = 'Pending'
            """,
            user_id=user_id,
        )[0][0]

        items_in_cart = [CartItems(row[0], row[1], row[2], row[3], row[4], row[5]) for row in rows]
        return items_in_cart, total_items


    @staticmethod
    @handle_db_exceptions
    def add_item(user_id, product_id, quantity, seller_id):
        """
        Adds an item to the cart after checking inventory.
        @param user_id: The user ID to add the item for.
        @param product_id: The product ID to add to the cart.
        @param quantity: The quantity of the product to add.
        @param seller_id: The seller ID associated with the product.
        """

        # 1. Check inventory
        available_quantity = CartItems._get_available_inventory(product_id, seller_id)
        if available_quantity is None:
            return "Product not found in inventory."
        if quantity > available_quantity:
            return "Not enough inventory available."

        # 2. Get unit price of the product
        unit_price = CartItems._get_product_price(product_id, seller_id)
        if unit_price is None:
            return "Product not found."

        # 3. Validation for if the product is already in the cart
        order_id = CartItems._get_or_create_pending_cart(user_id)
        existing_item = CartItems._get_existing_cart_item(order_id, product_id, seller_id)
        
        if existing_item:
            new_quantity = existing_item[0][0] + quantity
            if new_quantity > available_quantity:
                return "Not enough inventory available for the requested quantity."
            CartItems._update_cart_item(order_id, product_id, seller_id, new_quantity)
        else:
            CartItems._insert_cart_item(order_id, product_id, seller_id, quantity, unit_price)

        return "success"
    
    @staticmethod
    @handle_db_exceptions
    def delete_cart(user_id):
        """Deletes the entire cart and all items within it for the given user."""
        order_id = CartItems._get_pending_cart_id(user_id)
        
        if not order_id:
            return "No pending cart found."

        current_app.db.execute(
            """
            DELETE FROM Cart WHERE order_id = :order_id;
            """,
            order_id=order_id
        )
        return "success"

    @staticmethod
    @handle_db_exceptions
    def remove_item(user_id, product_id, seller_id):
        """
        Removes an item from the cart.
        @param user_id: The user ID to remove the item for.
        @param product_id: The product ID to remove from the cart.

        """
        order_id = CartItems._get_pending_cart_id(user_id)
        if order_id is None:
            return "No pending cart found."

        CartItems._delete_cart_item(order_id, product_id, seller_id)
        return "success"

    @staticmethod
    @handle_db_exceptions
    def update_item_quantity(user_id, product_id, seller_id, new_quantity):
        """
        Updates the quantity of an item in the cart.
        @param user_id: The user ID to update the item for.
        @param product_id: The product ID to update the quantity for.
        @param seller_id: The seller ID associated with the product.
        @param new_quantity: The new quantity of the product.
        """
        order_id = CartItems._get_pending_cart_id(user_id)
        if not order_id:
            return "No pending cart found."

        if new_quantity <= 0:
            return CartItems.remove_item(user_id, product_id, seller_id)

        if not CartItems._is_valid_quantity(product_id, seller_id, new_quantity):
            return "Not enough inventory available."

        CartItems._update_cart_item(order_id, product_id, seller_id, new_quantity)
        return "success"
    
    @staticmethod
    def apply_coupon_code(user_id, coupon_code):
        """Applies a coupon code to the user's pending cart."""

        order_id = CartItems._get_pending_cart_id(user_id)
        if not order_id:
            return "No pending cart found."

        discount_percentage = Coupons.get_discount(coupon_code)
        if discount_percentage is None:
            return "Invalid coupon code."

        current_app.db.execute(
            """
            UPDATE Cart
            SET coupon_code = :coupon_code
            WHERE order_id = :order_id
            """,
            coupon_code=coupon_code,
            order_id=order_id
        )
        return "success"

    @staticmethod
    def get_coupon_code(user_id):
        """Retrieves the coupon code associated with the user's pending cart."""
        coupon_code_row = current_app.db.execute(
            """
            SELECT coupon_code FROM Cart
            WHERE user_id = :user_id AND purchase_status = 'Pending'
            """,
            user_id=user_id
        )
        return coupon_code_row[0][0] if coupon_code_row else None

    @staticmethod
    def clear_coupon_code(user_id):
        """Clears the coupon code associated with the user's pending cart."""
        order_id = CartItems._get_pending_cart_id(user_id)
        if not order_id:
            return "No pending cart found."

        current_app.db.execute(
            """
            UPDATE Cart
            SET coupon_code = NULL
            WHERE order_id = :order_id
            """,
            order_id=order_id
        )
        return "success"

    @staticmethod
    def _get_available_inventory(product_id, seller_id):
        inventory_row = current_app.db.execute(
            """
            SELECT product_quantity FROM Products
            WHERE product_id = :product_id AND seller_id = :seller_id
            """,
            product_id=product_id,
            seller_id=seller_id,
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
    def _get_product_price(product_id, seller_id):
        price_row = current_app.db.execute(
            """
            SELECT price FROM Products WHERE product_id = :product_id AND seller_id =:seller_id
            """,
            product_id=product_id,
            seller_id=seller_id,
        )
        return price_row[0][0] if price_row else None

    @staticmethod
    def _get_existing_cart_item(order_id, product_id, seller_id):
        existing_item = current_app.db.execute(
            """
            SELECT quantity FROM CartProducts
            WHERE order_id = :order_id AND product_id = :product_id AND seller_id = :seller_id
            """,
            order_id=order_id,
            product_id=product_id,
            seller_id=seller_id,

        )
        return existing_item

    @staticmethod
    def _update_cart_item(order_id, product_id, seller_id, new_quantity):
        current_app.db.execute(
            """
            UPDATE CartProducts
            SET quantity = :new_quantity
            WHERE order_id = :order_id AND product_id = :product_id AND seller_id = :seller_id
            """,
            order_id=order_id,
            product_id=product_id,
            seller_id=seller_id,
            new_quantity=new_quantity,
        )


    @staticmethod
    def _insert_cart_item(order_id, product_id, seller_id, quantity, unit_price):
        current_app.db.execute(
            """
            INSERT INTO CartProducts (order_id, product_id, seller_id, quantity, unit_price)
            VALUES (:order_id, :product_id, :seller_id, :quantity, :unit_price)
            """,
            order_id=order_id,
            product_id=product_id,
            seller_id=seller_id,
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
    def _delete_cart_item(order_id, product_id, seller_id):
        current_app.db.execute(
            """
            DELETE FROM CartProducts
            WHERE order_id = :order_id AND product_id = :product_id AND seller_id = :seller_id
            """,
            order_id=order_id,
            product_id=product_id,
            seller_id=seller_id,
        )
    @staticmethod
    def _is_valid_quantity(product_id, seller_id, requested_quantity):
        available_quantity = CartItems._get_available_inventory(product_id, seller_id)
        return (
            available_quantity is not None and requested_quantity <= available_quantity
        )
