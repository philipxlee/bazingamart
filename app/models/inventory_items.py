from flask import current_app as app


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

    # Updated method to deactivate a specific product from the seller's inventory instead of deleting it
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
    def get_seller_orders(seller_id):
        rows = app.db.execute('''
        SELECT 
            o.order_id,
            u.firstname || ' ' || u.lastname AS buyer_name,
            u.address AS buyer_address,
            o.created_at AS order_date,
            SUM(cp.quantity * cp.unit_price) AS total_price,
            SUM(cp.quantity) AS total_items,
            cp.product_id,
            p.product_name AS product_name,
            cp.quantity AS item_quantity,
            o.fulfillment_status
        FROM orders o
        JOIN users u ON o.user_id = u.id
        JOIN cartproducts cp ON o.order_id = cp.order_id
        JOIN products p ON cp.product_id = p.product_id
        WHERE p.seller_id = :seller_id
        GROUP BY o.order_id, u.firstname, u.lastname, u.address, o.created_at, cp.product_id, p.product_name, cp.quantity, o.fulfillment_status
        ORDER BY o.created_at DESC
        ''', seller_id=seller_id)  

        # Organize rows by order and item details
        orders = {}
        for row in rows:
            order_id = row[0]
            if order_id not in orders:
                orders[order_id] = {
                    "order_id": order_id,
                    "buyer_name": row[1],
                    "buyer_address": row[2],
                    "order_date": row[3],
                    "total_price": row[4],
                    "total_items": row[5],
                    "items": []  # Ensure items is initialized as a list
                }
                
            # Append each product in the order to the items list
            orders[order_id]["items"].append({
                "product_id": row[6],
                "product_name": row[7],
                "quantity": row[8],
                "fulfillment_status": row[9]
            })

        return [order for order in orders.values()]
