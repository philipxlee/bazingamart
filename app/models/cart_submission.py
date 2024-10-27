from flask import current_app
from app.models.cart_items import CartItems


class CartSubmission:
    """
    This class handles the submission of the cart, including balance checks,
    inventory updates, and order creation.
    """

    @staticmethod
    def submit_cart(user_id):
        """
        Submits the cart as an order after checking product availability, user balance,
        and updating inventories and balances.
        @param user_id: The user ID submitting the order.
        """
        # 1. Fetch the user's cart items
        cart_items = CartItems.get_all_items(user_id)
        if not cart_items:
            return "Your cart is empty."

        # 2. Calculate total cart cost
        total_cost = sum(item.quantity * item.unit_price for item in cart_items)

        # 3. Check user balance
        user_balance = CartSubmission._get_user_balance(user_id)
        if user_balance < total_cost:
            return "Insufficient balance to complete the purchase."

        # 4. Check product availability
        for item in cart_items:
            available_quantity = CartItems._get_available_inventory(item.product_id)
            if available_quantity is None or available_quantity < item.quantity:
                return f"Not enough inventory for {item.product_name}."

        # 5. Deduct the total cost from user's balance
        CartSubmission._deduct_user_balance(user_id, total_cost)

        # 6. Update seller balances and inventory
        for item in cart_items:
            CartSubmission._decrease_inventory(item.product_id, item.quantity)
            seller_id = CartSubmission._get_seller_id(item.product_id)
            CartSubmission._increase_seller_balance(
                seller_id, item.quantity * item.unit_price
            )

        # 7. Mark cart as purchased (change purchase_status to 'Completed')
        CartSubmission._mark_cart_as_completed(user_id)

        # 8. Log the purchase in the Purchases table
        for item in cart_items:
            CartSubmission._log_purchase(
                user_id, item.product_id, item.quantity, item.unit_price
            )

        return "Purchase successful!"

    @staticmethod
    def _get_user_balance(user_id):
        balance_row = current_app.db.execute(
            """
            SELECT balance FROM Users WHERE id = :user_id
            """,
            user_id=user_id,
        )
        return balance_row[0][0] if balance_row else 0

    @staticmethod
    def _deduct_user_balance(user_id, amount):
        current_app.db.execute(
            """
            UPDATE Users
            SET balance = balance - :amount
            WHERE id = :user_id
            """,
            user_id=user_id,
            amount=amount,
        )

    @staticmethod
    def _increase_seller_balance(seller_id, amount):
        current_app.db.execute(
            """
            UPDATE Users
            SET balance = balance + :amount
            WHERE id = :seller_id
            """,
            seller_id=seller_id,
            amount=amount,
        )
    
    @staticmethod
    def _decrease_inventory(product_id, quantity):
        """
        Decreases the product's inventory by the given quantity.
        @param product_id: The ID of the product.
        @param quantity: The quantity to decrease.
        """
        current_app.db.execute(
            """
            UPDATE Inventory
            SET product_quantity = product_quantity - :quantity
            WHERE product_id = :product_id
            """,
            product_id=product_id,
            quantity=quantity
        )
    
    @staticmethod
    def _get_seller_id(product_id):
        """
        Returns the seller ID for the given product.
        @param product_id: The product ID.
        """
        seller_row = current_app.db.execute(
            """
            SELECT seller_id
            FROM Inventory
            WHERE product_id = :product_id
            """,
            product_id=product_id
        )
        return seller_row[0][0] if seller_row else None
    
    @staticmethod
    def _mark_cart_as_completed(user_id):
        """
        Marks the user's cart as completed after the order has been placed.
        @param user_id: The user ID whose cart should be marked as completed.
        """
        current_app.db.execute(
            """
            UPDATE Cart
            SET purchase_status = 'Completed'
            WHERE user_id = :user_id AND purchase_status = 'Pending'
            """,
            user_id=user_id
        )
    
    @staticmethod
    def _log_purchase(user_id, product_id, quantity, unit_price):
        """
        Logs a purchase in the Purchases table.
        @param user_id: The ID of the user making the purchase.
        @param product_id: The ID of the product being purchased.
        @param quantity: The quantity of the product being purchased.
        @param unit_price: The price of the product at the time of purchase.
        """
        current_app.db.execute(
            """
            INSERT INTO Purchases (uid, pid, quantity, price, time_purchased)
            VALUES (:user_id, :product_id, :quantity, :unit_price, current_timestamp)
            """,
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            unit_price=unit_price
        )

