from flask import current_app as app


class Reviews:
   def __init__(self, review_id, user_id, reviewer_type, product_id, stars, review_text, time_written, upvotes, images):
       self.review_id = review_id
       self.user_id = user_id
       self.reviewer_type = reviewer_type
       self.product_id = product_id
       self.stars = stars
       self.review_text = review_text
       self.time_written = time_written
       self.upvotes = upvotes
       self.images = images


   @staticmethod
   def get_recent_feedback(user_id, limit=5):
       rows = app.db.execute('''
           SELECT review_id, user_id, reviewer_type, product_id, stars, review_text, time_written
           FROM Reviews
           WHERE user_id = :user_id
           ORDER BY time_written DESC
           LIMIT :limit
       ''', user_id=user_id, limit=limit)
       return rows




   @staticmethod
   def add_review(user_id, reviewer_type, product_id, seller_id, stars, review_text, images=None):
       try:
           rows = app.db.execute('''
               INSERT INTO Reviews(user_id, reviewer_type, product_id, stars, review_text, images)
               VALUES(:user_id, :reviewer_type, :product_id, :stars, :review_text, :images)
               RETURNING review_id
           ''', user_id=user_id, reviewer_type=reviewer_type, product_id=product_id,
               stars=stars, review_text=review_text, images=images)
           review_id = rows[0][0]
           return review_id
       except Exception as e:
           print(str(e))
           return None


   @staticmethod
   def update_review(review_id, stars, review_text, images=None):
       try:
           app.db.execute('''
               UPDATE Reviews
               SET stars = :stars, review_text = :review_text, images = :images
               WHERE review_id = :review_id
           ''', review_id=review_id, stars=stars, review_text=review_text, images=images)
           return True
       except Exception as e:
           print(str(e))
           return False


   @staticmethod
   def delete_review(review_id):
       try:
           app.db.execute('''
               DELETE FROM Reviews
               WHERE review_id = :review_id
           ''', review_id=review_id)
           return True
       except Exception as e:
           print(str(e))
           return False


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
           SELECT review_id, user_id, reviewer_type, product_id, stars, review_text, time_written, upvotes, images
           FROM Reviews
           WHERE product_id = :product_id
           ORDER BY time_written DESC
           LIMIT :limit
       ''', product_id=product_id, limit=limit)
       return [Reviews(*row) for row in rows]


   @staticmethod
   def get_reviews_by_seller(seller_id, limit=10):
       rows = app.db.execute('''
           SELECT review_id, user_id, reviewer_type, product_id, stars, review_text, time_written, upvotes, images
           FROM Reviews
           WHERE seller_id = :seller_id
           ORDER BY time_written DESC
           LIMIT :limit
       ''', seller_id=seller_id, limit=limit)
       return [Reviews(*row) for row in rows]