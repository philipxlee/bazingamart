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
        SELECT p.seller_id, p.product_quantity
            FROM Products p
            WHERE p.product_id = :product_id
        ''', product_id=product_id)
        return [{"seller_id": row[0], "product_quantity": row[1]} for row in rows]

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

    # Updated method to mark a specific product as unavailable in the seller's inventory instead of deleting it
    @staticmethod
    def delete_inventory_item(seller_id, product_id):
        app.db.execute('''
        UPDATE Products
        SET available = FALSE
        WHERE seller_id = :seller_id AND product_id = :product_id
        ''', seller_id=seller_id, product_id=product_id)

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