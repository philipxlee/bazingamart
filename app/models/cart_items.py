from flask import current_app as app

class CartItems:
    """
    This class represents all the items within a user's cart. It provides API services
    to add, remove, and update items quantities from the cart. Additionally, it provides 
    a method to view the items and the total cost of all items in the cart.
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
        @param user_id: the user's id
        """

        # SQL query without joining the Products table
        rows = app.db.execute('''
            SELECT cp.product_id, cp.order_id, cp.quantity, cp.unit_price
            FROM CartProducts cp
            JOIN Cart c ON cp.order_id = c.order_id
            WHERE c.user_id = :user_id AND c.purchase_status = 'Pending'
        ''', user_id=user_id)

        items_in_cart = [CartItems(row[0], row[1], row[2], row[3]) for row in rows]
        return items_in_cart


    @staticmethod
    def add_item(user_id, product_id, quantity):
        """
        Adds an item to the cart.
        @param user_id: the user's id
        @param product_id: the product's id
        @param quantity: the quantity of the product

        NOTE: WILL HAVE TO ADD SELLER INVENTORY CHECKS
        """
        try:
            # 1. Get or create the user's pending cart
            rows = app.db.execute(
                '''
                SELECT order_id FROM Cart
                WHERE user_id = :user_id AND purchase_status = 'Pending'
                ''', 
                user_id=user_id
            )

            if rows:
                # Pending cart exists, get the order_id
                order_id = rows[0][0]
            else:
                # No pending cart, create a new one
                rows = app.db.execute(
                    '''
                    INSERT INTO Cart (user_id, total_price, purchase_status)
                    VALUES (:user_id, 0.0, 'Pending')
                    RETURNING order_id
                    ''', 
                    user_id=user_id
                )
                order_id = rows[0][0]

            # 2. Get the unit price of the product
            # NOTE: Remove this once product handles this
            price_rows = app.db.execute(
                '''
                SELECT price FROM Products WHERE id = :product_id
                ''', 
                product_id=product_id
            )
            unit_price = price_rows[0][0]

            # 3. Insert the item into CartProducts
            app.db.execute(
                '''
                INSERT INTO CartProducts (order_id, product_id, quantity, unit_price)
                VALUES (:order_id, :product_id, :quantity, :unit_price)
                ''', 
                order_id=order_id, 
                product_id=product_id, 
                quantity=quantity, 
                unit_price=unit_price
            )

            # 4. Commit the transaction
            app.db.commit()
            print("Item added to cart successfully.")
            return "success"

        except Exception as e:
            # In case of an error, rollback the transaction
            app.logger.error(f"Failed to add item to cart: {str(e)}")
            app.db.rollback()
            return "failure"


    @staticmethod
    def get_total_cost(user_id) -> float:
        """
        Returns the total cost of all items in the cart
        @param user_id: the user's id
        """
        pass

    @staticmethod
    def remove_item(product_id):
        """
        Removes an item from the cart
        @param product_id: the product's id
        """
        pass
    
    @staticmethod
    def update_item_quantity(product_id, delta):
        """
        Updates the quantity of an item in the cart
        @param product_id: the product's id
        """
        pass



        