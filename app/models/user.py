from flask_login import UserMixin
from flask import current_app as app
from werkzeug.security import generate_password_hash, check_password_hash

from .. import login


class User(UserMixin):
    def __init__(self, id, email, firstname, lastname, balance, seller=False):
        self.id = id
        self.email = email
        self.firstname = firstname
        self.lastname = lastname
        self.balance = balance
        self.seller = seller

    @staticmethod
    def get_by_auth(email, password):
        rows = app.db.execute("""
SELECT password, id, email, firstname, lastname, balance
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
INSERT INTO Users(email, password, firstname, lastname, balance)
VALUES(:email, :password, :firstname, :lastname, :balance)
RETURNING id
""",
                                  email=email,
                                  password=generate_password_hash(password),
                                  firstname=firstname, lastname=lastname, 
                                  balance=balance)
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
SELECT id, email, firstname, lastname, balance
FROM Users
WHERE id = :id
""",
                              id=id)
        return User(*(rows[0])) if rows else None
    
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
    def update_info(uid, email, password, firstname, lastname):
        app.db.execute(
            """
            UPDATE Users
            SET firstname = :firstname,
            lastname= :lastname,
            email= :email,
            password= :password
            WHERE id = :uid
            """,
            uid=uid,
            firstname=firstname,
            lastname=lastname,
            email=email,
            password=generate_password_hash(password)
        )
        
    @staticmethod
    def update_info(uid, email, firstname, lastname):
        app.db.execute(
            """
            UPDATE Users
            SET firstname = :firstname,
            lastname= :lastname,
            email= :email
            WHERE id = :uid
            """,
            uid=uid,
            firstname=firstname,
            lastname=lastname,
            email=email,
        )
