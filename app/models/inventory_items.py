from flask import current_app as app
from app.models.orders import Order
from app.models.helpers.db_exceptions_wrapper import handle_db_exceptions

class InventoryItems:
    def __init__(self, product_id, product_name, product_quantity, product_price=None, available=True):
        self.product_id = product_id
        self.product_name = product_name
        self.product_quantity = product_quantity
        self.product_price = product_price
        self.available = available

    @staticmethod
    def get_all_by_user(seller_id):
        rows = app.db.execute('''
        SELECT p.product_id, p.product_name, p.product_quantity, p.price, p.available
            FROM Products p
            WHERE p.seller_id = :seller_id AND p.available = TRUE
            ORDER BY p.product_id ASC
        ''', seller_id=seller_id)
        items_in_inventory = [InventoryItems(row[0], row[1], row[2], row[3], row[4]) for row in rows]
        return items_in_inventory
    
    @staticmethod
    def get_all_by_product(product_id):
        rows = app.db.execute('''
        SELECT p.seller_id, p.product_quantity, p.price
            FROM Products p
            WHERE p.product_id = :product_id
        ''', product_id=product_id)
        return [{"seller_id": row[0], "product_quantity": row[1], "price": row[2]} for row in rows]



    # Updated method to fetch detailed information for a specific product in the seller's inventory
    @staticmethod
    def get_detailed_inventory_item(seller_id, product_id):
        row = app.db.execute('''
        SELECT p.product_id, p.product_name, p.product_quantity, p.price, p.available
            FROM Products p
            WHERE p.seller_id = :seller_id AND p.product_id = :product_id
        ''', seller_id=seller_id, product_id=product_id)

        return InventoryItems(*row[0]) if row else None

    # Added method to update the quantity of a specific product in the seller's inventory
    @staticmethod
    def update_inventory_item_quantity(seller_id, product_id, new_quantity):
        app.db.execute('''
        UPDATE Products
        SET product_quantity = :new_quantity
        WHERE seller_id = :seller_id AND product_id = :product_id
        ''', seller_id=seller_id, product_id=product_id, new_quantity=new_quantity)

    # Added method to update the price of a specific product in the seller's inventory
    @staticmethod
    def update_inventory_item_price(seller_id, product_id, new_price):
        app.db.execute('''
        UPDATE Products
        SET price = :new_price
        WHERE seller_id = :seller_id AND product_id = :product_id
        ''', seller_id=seller_id, product_id=product_id, new_price=new_price)

    @staticmethod
    def delete_inventory_item(seller_id, product_id):
        """
        Marks a specific product as unavailable in the seller's inventory instead of deleting it.
        Adds error handling and ensures the product exists before updating.
        """
        # Check if the product exists for the given seller
        product = app.db.execute('''
        SELECT product_id
        FROM Products
        WHERE seller_id = :seller_id AND product_id = :product_id
        ''', seller_id=seller_id, product_id=product_id)

        if not product:
            # If the product does not exist, raise an exception
            raise ValueError(f"No product found with ID {product_id} for seller {seller_id}.")

        # Update the product to set available = FALSE
        app.db.execute('''
        UPDATE Products
        SET available = FALSE
        WHERE seller_id = :seller_id AND product_id = :product_id
        ''', seller_id=seller_id, product_id=product_id)

    
    @staticmethod
    @handle_db_exceptions
    def add_new_product(seller_id, product_name, product_price, product_quantity):
        """
        Adds a new product to the seller's inventory in the Products table.
        Checks if a product with the same name already exists for the seller.
        """
        # Check for an existing product with the same name for the seller
        existing_product = app.db.execute('''
        SELECT product_id
        FROM Products
        WHERE product_name = :product_name AND seller_id = :seller_id
        ''', product_name=product_name, seller_id=seller_id)

        if existing_product:
            # Raise a ValueError if a duplicate is found
            raise ValueError(f"A product with the name '{product_name}' already exists in your inventory.")

        # If no duplicate, proceed to add the product
        app.db.execute('''
        INSERT INTO Products (product_name, price, available, seller_id, product_quantity)
        VALUES (:product_name, :product_price, TRUE, :seller_id, :product_quantity)
        ''', product_name=product_name, product_price=product_price, seller_id=seller_id, product_quantity=product_quantity)



    @staticmethod
    def get_paginated_by_user(seller_id, page, items_per_page):
        offset = (page - 1) * items_per_page
        rows = app.db.execute('''
        SELECT p.product_id, p.product_name, p.product_quantity, p.price, p.available
            FROM Products p
            WHERE p.seller_id = :seller_id AND p.available = TRUE
            ORDER BY p.product_id ASC
            LIMIT :items_per_page OFFSET :offset
        ''', seller_id=seller_id, items_per_page=items_per_page, offset=offset)
        items_in_inventory = [InventoryItems(row[0], row[1], row[2], row[3], row[4]) for row in rows]
        return items_in_inventory

    @staticmethod
    def get_count_by_user(seller_id):
        row = app.db.execute('''
        SELECT COUNT(*)
            FROM Products p
            WHERE p.seller_id = :seller_id AND p.available = TRUE
        ''', seller_id=seller_id)
        return row[0][0] if row else 0

    @staticmethod
    def get_seller_orders(seller_id, page, per_page):
        """
        Retrieves paginated orders for products sold by a given seller.
        """
        offset = (page - 1) * per_page
        rows = app.db.execute('''
            SELECT o.order_id, o.total_price, o.created_at, o.coupon_code
            FROM Orders o
            JOIN CartProducts cp ON o.order_id = cp.order_id
            WHERE cp.seller_id = :seller_id
            GROUP BY o.order_id
            ORDER BY o.created_at DESC
            LIMIT :per_page OFFSET :offset
        ''', seller_id=seller_id, per_page=per_page, offset=offset)
        return [Order(row[0], row[1], row[2], row[3]) for row in rows]

    @staticmethod
    def count_seller_orders(seller_id):
        """
        Counts the total number of orders for products sold by a given seller.
        """
        result = app.db.execute('''
            SELECT COUNT(DISTINCT o.order_id)
            FROM Orders o
            JOIN CartProducts cp ON o.order_id = cp.order_id
            WHERE cp.seller_id = :seller_id
        ''', seller_id=seller_id)
        return result[0][0] if result else 0
    
    @staticmethod
    def get_top_most_popular_products(seller_id, limit=3):
        """
        Retrieves the top N most popular products for a seller.
        """
        rows = app.db.execute('''
        SELECT p.product_id, p.product_name, SUM(cp.quantity) AS total_quantity
        FROM CartProducts cp
        JOIN Products p ON cp.product_id = p.product_id
        WHERE p.seller_id = :seller_id
        GROUP BY p.product_id, p.product_name
        ORDER BY total_quantity DESC
        LIMIT :limit
        ''', seller_id=seller_id, limit=limit)
        
        return [{"product_id": row[0], "product_name": row[1], "quantity_ordered": row[2]} for row in rows]

    @staticmethod
    def get_top_least_popular_products(seller_id, limit=3):
        """
        Retrieves the top N least popular products for a seller.
        """
        rows = app.db.execute('''
        SELECT p.product_id, p.product_name, SUM(cp.quantity) AS total_quantity
        FROM CartProducts cp
        JOIN Products p ON cp.product_id = p.product_id
        WHERE p.seller_id = :seller_id
        GROUP BY p.product_id, p.product_name
        ORDER BY total_quantity ASC
        LIMIT :limit
        ''', seller_id=seller_id, limit=limit)
        
        return [{"product_id": row[0], "product_name": row[1], "quantity_ordered": row[2]} for row in rows]
