from flask import current_app as app


class InventoryItems:
    def __init__(self, product_id, product_name, product_quantity):
        self.product_id = product_id
        self.product_name = product_name
        self.product_quantity = product_quantity


    @staticmethod
    def get_all_by_user(seller_id):
        rows = app.db.execute('''
        SELECT p.product_id, p.product_name, p.product_quantity
            FROM Products p
            WHERE p.seller_id = :seller_id
        ''', seller_id=seller_id)
        items_in_inventory = [InventoryItems(row[0], row[1], row[2]) for row in rows]
        return items_in_inventory

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
        ''', seller_id = seller_id)  

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
                    "items": []
                }
            # Append each product in the order to the items list
            orders[order_id]["items"].append({
                "product_id": row[6],
                "product_name": row[7],
                "quantity": row[8],
                "fulfillment_status": row[9]
            })

        return list(orders.values())