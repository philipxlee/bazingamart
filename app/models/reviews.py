from flask import current_app as app

class Reviews:
    def __init__(self, review_id, user_id, seller_id, reviewer_type, product_id, stars, review_text, time_written, upvotes, firstname, lastname):
        self.review_id = review_id
        self.user_id = user_id
        self.seller_id = seller_id
        self.reviewer_type = reviewer_type
        self.product_id = product_id
        self.stars = stars
        self.review_text = review_text
        self.time_written = time_written
        self.upvotes = upvotes
        self.firstname = firstname
        self.lastname = lastname

    
    @staticmethod
    def get(review_id):
        rows = app.db.execute('''
        SELECT review_id, user_id, product_id, stars, review_text, seller_id, reviewer_type, 
               time_written, upvotes
        FROM Reviews
        WHERE review_id = :review_id
        ''', review_id=review_id)

        # If a row is returned, create a Review object, otherwise return None
        if rows:
            # Add default values for missing firstname and lastname
            return Reviews(*rows[0], firstname=None, lastname=None)  
        return None
    
    @staticmethod
    def get_recent_feedback(user_id):
        rows = app.db.execute('''
            SELECT review_id, user_id, reviewer_type, product_id, stars, review_text, time_written
            FROM Reviews
            WHERE user_id = :user_id
            ORDER BY time_written DESC
        ''', user_id=user_id)
        return rows
    
    @staticmethod
    def get_reviews_received_by_seller(seller_id):
        rows = app.db.execute('''
            SELECT review_id, user_id, reviewer_type, product_id, stars, review_text, time_written
            FROM Reviews
            WHERE reviewer_type = 'seller' AND seller_id = :seller_id
            ORDER BY time_written DESC
        ''', seller_id=seller_id)
        return rows



    @staticmethod
    def add_review(user_id, product_id, stars, review_text, seller_id):
        """Insert a new review into the Reviews table with reviewer_type set to 'product'."""
        reviewer_type = 'product'  # Set reviewer_type explicitly for a product review
        
        result = app.db.execute('''
            INSERT INTO Reviews (user_id, product_id, stars, review_text, seller_id, reviewer_type, time_written)
            VALUES (:user_id, :product_id, :stars, :review_text, :seller_id, :reviewer_type, current_timestamp)
            RETURNING review_id
        ''', user_id=user_id, product_id=product_id, stars=stars, review_text=review_text, seller_id=seller_id, reviewer_type=reviewer_type)

        # If the insert was successful
        return result[0][0] if result else None

    
    @staticmethod
    def add_seller_review(seller_id, reviewer_id, stars, review_text):
        """
        Adds a new review for a seller.
        """
        app.db.execute('''
            INSERT INTO Reviews (seller_id, user_id, reviewer_type, stars, review_text, time_written, product_id)
            VALUES (:seller_id, :reviewer_id, 'seller', :stars, :review_text, NOW(), NULL)
        ''', 
        seller_id=seller_id, 
        reviewer_id=reviewer_id, 
        stars=stars, 
        review_text=review_text)




    @staticmethod
    def edit_review(review_id, stars, review_text):
        try:
            app.db.execute('''
                UPDATE Reviews
                SET stars = :stars, review_text = :review_text, time_written = current_timestamp
                WHERE review_id = :review_id
            ''', review_id=review_id, stars=stars, review_text=review_text)
            return True
        except Exception as e:
            print(str(e))
        return False


    @staticmethod
    def get_review_by_id(review_id):
        """Fetches a review by its ID."""
        result = app.db.execute('''
            SELECT * FROM Reviews WHERE review_id = :review_id
        ''', review_id=review_id)
        return result[0] if result else None

    @staticmethod
    def delete_review(review_id):
        """Deletes a review by its ID."""
        rows_deleted = app.db.execute('''
            DELETE FROM Reviews WHERE review_id = :review_id
        ''', review_id=review_id)
        
        # Check if any rows were affected
        return rows_deleted > 0

    @staticmethod
    def upvote_review(review_id):
        try:
            app.db.execute('''
                UPDATE Reviews
                SET upvotes = upvotes + 1
                WHERE review_id = :review_id
            ''', review_id=review_id)
            return True
        except Exception as e:
            print(str(e))
            return False
        
    @staticmethod
    def get_reviews_by_product(product_id, limit=10):
        rows = app.db.execute('''
            SELECT 
                r.review_id, r.user_id, r.seller_id, r.reviewer_type, 
                r.product_id, r.stars, r.review_text, r.time_written, r.upvotes,
                u.firstname, u.lastname
            FROM Reviews r
            JOIN Users u ON r.user_id = u.id
            WHERE r.product_id = :product_id
            ORDER BY r.time_written DESC
            LIMIT :limit
    ''', product_id=product_id, limit=limit)
        return [Reviews(*row) for row in rows]

    @staticmethod
    def get_review_by_user_and_product(user_id, product_id):
        # Execute a query to check if a review exists for the given user and product
        rows = app.db.execute('''
            SELECT review_id
            FROM Reviews
            WHERE user_id = :user_id AND product_id = :product_id
            LIMIT 1
        ''', user_id=user_id, product_id=product_id)

        # If rows is not empty, a review already exists
        return rows[0] if rows else None  # Return the first row if a review is found, else None

    @staticmethod
    def get_reviews_by_seller(seller_id, limit=10):
        rows = app.db.execute('''
            SELECT review_id, user_id, reviewer_type, product_id, stars, review_text, time_written, upvotes
            FROM Reviews
            WHERE seller_id = :seller_id
            ORDER BY time_written DESC
            LIMIT :limit
        ''', seller_id=seller_id, limit=limit)
        return [Reviews(*row) for row in rows]
    
    @staticmethod
    def get_average_rating(product_id):
        """Calculate the average rating for a product."""
        result = app.db.execute('''
            SELECT COALESCE(AVG(stars), 0) AS average_rating
            FROM Reviews
            WHERE product_id = :product_id
        ''', product_id=product_id)
    
        return result[0]['average_rating'] if result else 0

