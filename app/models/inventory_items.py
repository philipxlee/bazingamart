from flask import current_app as app


class InventoryItems:
    def __init__(self, product_id, product_name, product_quantity):
        'self.seller_id = seller_id'
        self.product_id = product_id
        self.product_name = product_name
        self.product_quantity = product_quantity

    
    @staticmethod
    def get_all_by_user(seller_id):
        rows = app.db.execute('''
        SELECT i.product_id, i.product_name, i.product_quantity
            FROM Inventory i
            WHERE i.seller_id = :seller_id
        ''', seller_id=seller_id)
        items_in_inventory = [InventoryItems(row[0], row[1], row[2]) for row in rows]
        return items_in_inventory

