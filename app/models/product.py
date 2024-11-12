from flask import current_app as app

class Product:
    def __init__(self, product_id, product_name, price, available):
        self.product_id = product_id
        self.product_name = product_name
        self.price = price
        self.available = available

    @staticmethod
    def get(product_id):
        rows = app.db.execute('''
        SELECT product_id, product_name, price, available
        FROM Products
        WHERE product_id = :product_id
        ''',
                              id=id)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all(available=True):
        rows = app.db.execute('''
            SELECT product_id, product_name, price, available
            FROM Products
            WHERE available = :available
        ''',
        available=available)
        return [Product(*row) for row in rows]
    
    @staticmethod
    def get_top_k_expensive(k):
        rows = app.db.execute('''
            SELECT product_id, product_name, price, available
            FROM Products
            ORDER BY price DESC
            LIMIT :k
            ''',
                                 k=k)
        return [Product(*row) for row in rows]
