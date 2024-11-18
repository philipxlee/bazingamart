from flask import current_app
from app.models.cart_items import CartItems
from app.models.helpers.db_exceptions_wrapper import handle_db_exceptions
from app.models.user import User
from app.models.coupons import Coupons
from flask_login import current_user
from decimal import Decimal

class CartSubmission:
    """
    This class handles the submission of the cart, including balance checks,
    inventory updates, and order creation.
    """

    @staticmethod
    @handle_db_exceptions
    def submit_cart(user_id):
        """
        Submits the cart as an order after checking product availability, user balance,
        and updating inventories and balances.
        @param user_id: The user ID submitting the order.
        """
        # 1. Fetch the user's cart items
        cart_items = CartItems.get_all_cart_items(user_id)
        if not cart_items:
            return "Your cart is empty."

        # 2. Calculate total cart cost and apply coupons if applicable
        total_cost = sum(Decimal(item.quantity) * item.unit_price for item in cart_items)
        coupon_code = CartItems.get_coupon_code(user_id)
        discount_percentage = 0
        discount_amount = Decimal('0.00')
        if coupon_code:
            discount_percentage = Coupons.get_discount(coupon_code) or 0
            discount_rate = Decimal(discount_percentage) / Decimal('100')
            discount_amount = total_cost * discount_rate
            total_cost -= discount_amount

        # 3. Check user balance
        user_balance = User.get_balance(user_id)
        if user_balance < total_cost:
            return "Insufficient balance to complete the purchase."

        # 4. Check product availability
        for item in cart_items:
            available_quantity = CartItems._get_available_inventory(item.product_id)
            if available_quantity is None or available_quantity < item.quantity:
                return f"Not enough inventory for {item.product_name}."

        # 5. Deduct the total cost from user's balance
        deduct_total = -1 * total_cost
        User.update_balance(user_id, deduct_total)

        # 6. Update seller balances and inventory
        for item in cart_items:
            CartSubmission._decrease_inventory(item.product_id, item.quantity)
            seller_id = CartSubmission._get_seller_id(item.product_id)
            CartSubmission._increase_seller_balance(
                seller_id, item.quantity * item.unit_price
            )

        # 7. Check if an order already exists
        order_id = CartItems._get_pending_cart_id(user_id)
        result = current_app.db.execute(
            """
            SELECT 1 FROM Orders WHERE order_id = :order_id
            """,
            order_id=order_id
        )
        existing_order = result[0] if result else None

        # 8. Insert or update the order as necessary
        if existing_order is None:
            # Order does not exist, create a new one
            current_app.db.execute(
                """
                INSERT INTO Orders (order_id, user_id, created_at, total_price, fulfillment_status, coupon_code)
                VALUES (:order_id, :user_id, current_timestamp, :total_price, 'Incomplete', :coupon_code)
                """,
                order_id=order_id,
                user_id=user_id,
                total_price=total_cost,
                coupon_code=coupon_code
            )
        else:
            # Order exists, optionally update its status
            current_app.db.execute(
                """
                UPDATE Orders
                SET fulfillment_status = 'Incomplete', total_price = :total_price, coupon_code = :coupon_code
                WHERE order_id = :order_id
                """,
                order_id=order_id,
                total_price=total_cost,
                coupon_code=coupon_code
            )


        # 9. Mark cart as purchased (change purchase_status to 'Completed')       
        CartSubmission._mark_cart_as_completed(user_id)
        return "Purchase successful!"

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
        current_app.db.execute(
            """
            UPDATE Products
            SET product_quantity = product_quantity - :quantity
            WHERE product_id = :product_id
            """,
            product_id=product_id,
            quantity=quantity
        )
    
    @staticmethod
    def _get_seller_id(product_id):
        seller_row = current_app.db.execute(
            """
            SELECT seller_id
            FROM Products
            WHERE product_id = :product_id
            """,
            product_id=product_id
        )
        return seller_row[0][0] if seller_row else None
    
    @staticmethod
    def _mark_cart_as_completed(user_id):
        current_app.db.execute(
            """
            UPDATE Cart
            SET purchase_status = 'Completed'
            WHERE user_id = :user_id AND purchase_status = 'Pending'
            """,
            user_id=user_id
        )
    
