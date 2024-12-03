from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash
from app.models.cart_items import CartItems

from .. import login


class User(UserMixin):
    def __init__(self, id, email, firstname, lastname, balance, seller, address):
        self.id = id
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.balance = balance
        self.seller = seller
        self.address = address

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT password, id, email, firstname, lastname, balance, seller, address
FROM Users
WHERE email = :email
""",
                              email=email)
        if not rows:  # email not found
            return None
        elif not check_password_hash(rows[0][0], password):
            # incorrect password
            return None
        else:
            return User(*(rows[0][1:]))

    @staticmethod
    def email_exists(email):
        rows = app.db.execute("""
SELECT email
FROM Users
WHERE email = :email
""",
                              email=email)
        return len(rows) > 0

    @staticmethod
    def register(email, password, firstname, lastname):
        try:
            balance = 0.0
            rows = app.db.execute("""
INSERT INTO Users(email, password, firstname, lastname)
VALUES(:email, :password, :firstname, :lastname)
RETURNING id
""",
                                  email=email,
                                  password=generate_password_hash(password),
                                  firstname=firstname, lastname=lastname)
            id = rows[0][0]
            return User.get(id)
        except Exception as e:
            # likely email already in use; better error checking and reporting needed;
            # the following simply prints the error to the console:
            print(str(e))
            return None

    @staticmethod
    @login.user_loader
    def get(id):
        rows = app.db.execute("""
        SELECT id, email, firstname, lastname, balance, seller, address
        FROM Users
        WHERE id = :id
        """, id=id)
        
        if rows:
            # Explicitly unpack the columns into variables
            id, email, firstname, lastname, balance, seller, address = rows[0]
            # If address is None, assign a default value
            address = address or "No address provided"
            return User(id, email, firstname, lastname, balance, seller, address)
        return None

    @staticmethod
    def get_balance(uid):
        bal = app.db.execute(
            """
            SELECT balance
            FROM Users
            WHERE id = :uid
            """,
            uid=uid,
        )
        return bal[0][0] if bal else 0
    
    @staticmethod
    def get_address(uid):
        addr = app.db.execute(
            """
            SELECT address
            FROM Users
            WHERE id = :uid
            """,
            uid=uid,
        )
        return addr[0][0] if addr else 0
    
    @staticmethod
    def update_balance(uid, amount):
        app.db.execute(
            """
            UPDATE Users
            SET balance = balance + :amount
            WHERE id = :uid
            """,
            uid=uid,
            amount=amount
        )
        
    @staticmethod
    def update_info(uid, email, password, firstname, lastname, address):
        if password:
            app.db.execute(
                """
                UPDATE Users
                SET firstname = :firstname,
                lastname= :lastname,
                email= :email,
                address= :address,
                password= :password
                WHERE id = :uid
                """,
                uid=uid,
                firstname=firstname,
                lastname=lastname,
                email=email,
                address=address,
                password=generate_password_hash(password)
            )
        else:
            app.db.execute(
                """
                UPDATE Users
                SET firstname = :firstname,
                lastname= :lastname,
                email= :email,
                address= :address
                WHERE id = :uid
                """,
                uid=uid,
                firstname=firstname,
                lastname=lastname,
                email=email,
                address=address
            )
            
            
    @staticmethod
    def average_spent(uid):
        # Import here to remove circular Import
        from app.models.orders import Order 
        
        total_money = app.db.execute(
            """
            SELECT COALESCE(SUM(total_price), 0) AS total_money
            FROM Orders
            WHERE user_id = :uid
            """,
            uid=uid,
        )[0][0]  
        
        total_orders = Order.count_orders(uid)
        
        if total_orders > 0:
            average = total_money / total_orders
        else:
            average = 0
        
        return round(average, 2)
    
    @staticmethod
    def max_order_price(uid):
        result = app.db.execute(
            """
            SELECT MAX(total_price)
            FROM Orders 
            WHERE user_id = :uid
            """,
            uid=uid,
        )
        return result[0][0] if result else 0
    
    @staticmethod
    def min_order_price(uid):
        result = app.db.execute(
            """
            SELECT MIN(total_price)
            FROM Orders 
            WHERE user_id = :uid
            """,
            uid=uid,
        )
        return result[0][0] if result else 0
    
    
