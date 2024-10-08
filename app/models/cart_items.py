from flask import current_app as app

class CartItems:
    """
    This class represents all the items within a user's cart. It provides API services
    to add, remove, and update items quantities from the cart. Additionally, it provides 
    a method to view the items and the total cost of all items in the cart.
    """
    def __init__(self, product_id, order_id, quantity, unit_price):
        self.product_id = product_id
        self.order_id = order_id
        self.quantity = quantity
        self.unit_price = unit_price

    @staticmethod
    def get_all_items(user_id) -> list:
        """
        Returns all items in the cart
        @param user_id: the user's id
        """
        pass
    
    @staticmethod
    def get_total_cost(user_id) -> float:
        """
        Returns the total cost of all items in the cart
        @param user_id: the user's id
        """
        pass

    @staticmethod
    def add_item(user_id, product_id, quantity):
        """
        Adds an item to the cart
        @param user_id: the user's id
        @param product_id: the product's id
        @param quantity: the quantity of the product
        """
        pass

    @staticmethod
    def remove_item(product_id):
        """
        Removes an item from the cart
        @param product_id: the product's id
        """
        pass
    
    @staticmethod
    def update_item_quantity(product_id, delta):
        """
        Updates the quantity of an item in the cart
        @param product_id: the product's id
        """
        pass



        