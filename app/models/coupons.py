from flask import current_app

class Coupons:
    @staticmethod
    def get_discount(coupon_code):
        """
        Retrieves the discount percentage for a valid coupon code.
        Returns the discount percentage if valid, else returns None.
        """
        coupon = current_app.db.execute(
            """
            SELECT discount_percentage
            FROM Coupons
            WHERE coupon_code = :coupon_code
            """,
            coupon_code=coupon_code
        )
        return coupon[0][0] if coupon else None