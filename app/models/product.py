from flask import current_app as app
from math import ceil

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
                              product_id=product_id)
        return Product(*(rows[0])) if rows is not None else None

    @staticmethod
    def get_all(available=True, page=1, per_page=9):
        offset = (page - 1) * per_page
        rows = app.db.execute(
            '''
            SELECT product_id, product_name, price, available
            FROM Products
            WHERE available = :available
            LIMIT :per_page OFFSET :offset
            ''',
            available=available, 
            per_page=per_page, 
            offset=offset
        )
        
        total_count = app.db.execute(
            '''
            SELECT COUNT(*) FROM Products WHERE available = :available
            ''', 
            available=available
        )[0][0]
        
        total_pages = ceil(total_count / per_page)
        return [Product(*row) for row in rows], total_pages

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
