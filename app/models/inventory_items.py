from flask import current_app as app

class InventoryItems:
    """
    This class represents all items in a seller's inventory. It provides API services
    to add, remove, and update item quantities in the inventory. Additionally, it provides
    a method to view all inventory items for a specific seller.
    """
    def __init__(self, product_id, product_name, seller_id, product_quantity):
        self.product_id = product_id
        self.product_name = product_name
        self.seller_id = seller_id
        self.product_quantity = product_quantity

    @staticmethod
    def get_all_items(seller_id) -> list:
        """
        Returns all inventory items for the given seller.
        @param seller_id: the seller's id
        """

        # Query the Inventory table to get all products for a seller
        rows = app.db.execute('''
            SELECT product_id, product_name, seller_id, product_quantity
            FROM Inventory
            WHERE seller_id = :seller_id
        ''', seller_id=seller_id)

        # Create a list of InventoryItems from the query result
        items_in_inventory = [InventoryItems(row[0], row[1], row[2], row[3]) for row in rows]
        return items_in_inventory

    @staticmethod
    def add_item(seller_id, product_name, product_quantity):
        """
        Adds a new item to the seller's inventory.
        @param seller_id: the seller's id
        @param product_name: the name of the product
        @param product_quantity: the quantity of the product to add
        """
        try:
            # Insert a new product into the Inventory
            app.db.execute(
                '''
                INSERT INTO Inventory (product_name, seller_id, product_quantity)
                VALUES (:product_name, :seller_id, :product_quantity)
                ''', 
                product_name=product_name, 
                seller_id=seller_id, 
                product_quantity=product_quantity
            )
            
            app.db.commit()
            print("Item added to inventory successfully.")
            return "success"

        except Exception as e:
            # Rollback the transaction in case of an error
            app.logger.error(f"Failed to add item to inventory: {str(e)}")
            app.db.rollback()
            return "failure"

    @staticmethod
    def update_item_quantity(seller_id, product_id, new_quantity):
        """
        Updates the quantity of a product in the inventory.
        @param seller_id: the seller's id
        @param product_id: the product's id
        @param new_quantity: the new quantity to set
        """
        try:
            app.db.execute(
                '''
                UPDATE Inventory
                SET product_quantity = :new_quantity
                WHERE seller_id = :seller_id AND product_id = :product_id
                ''', 
                new_quantity=new_quantity, 
                seller_id=seller_id, 
                product_id=product_id
            )

            app.db.commit()
            print("Product quantity updated successfully.")
            return "success"
        
        except Exception as e:
            app.logger.error(f"Failed to update product quantity: {str(e)}")
            app.db.rollback()
            return "failure"

    @staticmethod
    def remove_item(seller_id, product_id):
        """
        Removes an item from the inventory.
        @param seller_id: the seller's id
        @param product_id: the product's id
        """
        try:
            app.db.execute(
                '''
                DELETE FROM Inventory
                WHERE seller_id = :seller_id AND product_id = :product_id
                ''', 
                seller_id=seller_id, 
                product_id=product_id
            )
            
            app.db.commit()
            print("Item removed from inventory successfully.")
            return "success"
        
        except Exception as e:
            app.logger.error(f"Failed to remove item from inventory: {str(e)}")
            app.db.rollback()
            return "failure"
