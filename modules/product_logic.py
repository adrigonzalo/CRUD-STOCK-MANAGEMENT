"""
In this script only include code related to validation and bussiness logic
"""

import sqlite3

class ProductLogic:

    # Constructor
    def __init__(self, db_manager):
        self.db = db_manager

    
    # -- BUSSINESS LOGIC --

    # Search products function
    def search_product(self, search_term):

        # Query
        query = 'SELECT * FROM products WHERE name = ?'

        # Parameters
        parameters = ('{}'.format(search_term),)

        return self.db.run_query(query, parameters)
    
    # Get products function:
    def get_products(self):

        query = 'SELECT * FROM products ORDER BY name DESC'

        return self.db.run_query(query)
    
    # Get categories function
    def get_categories(self):

        # Select all the categories
        query = 'SELECT * FROM categories ORDER BY name DESC'

        db_rows = self.db.run_query(query)

        # For loop to get all the categories
        try:
            categories = []
            for row in db_rows:
                categories.append(row[0])
        except Exception:
            pass # If it fails return an empty list

        return categories


    # Validation function
    def validation(self, name, price):
        # Validate if name or price inputs are not empty
        if not name or not price:
            return False, 'Name and price inputs are required.'
        
        # Validate if price input has a valid number
        try:
            price_value = float(price)
        except ValueError as ve:
            print(ve)
            return False, 'Price input must be a valid number.'
        
        # Validate if price input has a positive value
        if price_value <= 0:
            return False, "Price input must have a positive value."
        
        return True, '' 
    
    # Add product function
    def add_product(self, name, price, stock, category_name):
        
        # 1. Validation
        is_valid, error_msg = self.validation(name, price)
        if not is_valid:
            return False, error_msg
        
        # 2. Data Normalization
        name_normalized = name.capitalize()
        
        # 3. Look for the category_id record in the categories table
        query_cat = 'SELECT id FROM categories WHERE name = ?'
        res_cat = self.db.run_query(query_cat,(category_name,))
        
        try:

            row = res_cat.fetchone()
            category_id = row[0] if row else 1 # Use ID 1 if it doesnt find anything

        except Exception:
            category_id = 1

        # 4. Query
        # We insert default values in the new columns until create the widgets
        query = 'INSERT INTO products VALUES(NULL, ?, ?, ?, "No description", ?, 1)'

        # Parameters to use the run_query() function
        parameters = (name_normalized, price, stock, category_id)
        
        try:

            # Execute run_query
            self.db.run_query(query, parameters)
            return True, 'Product {} added successfully.'.format(name_normalized)

        except sqlite3.IntegrityError:
            
            return False, 'Product {} already exists (Database Error).'.format(name_normalized)
                
    # Delete product function
    def delete_product(self, name):
        try:

            # Query
            query = 'DELETE FROM products WHERE name = ?'

            # Execute run_query
            self.db.run_query(query,(name,))

            return True, '{} had been deleted successfully.'.format(name)
        
        except IndexError as ie:

            print('Error: ', ie)

            # Adding that, we can make sure that you cant try to delete anything in the database if the selection failed.
            return False, '{} doesnt exists.'.format(name)

    # Edit product function
    def update_product(self, new_name, new_price, old_name):
        
        try:
            # New Name
            final_name = new_name.capitalize()

            # Query
            query = 'UPDATE products SET name = ?, price = ? WHERE name = ?'

            parameters = (final_name, new_price, old_name) 

            self.db.run_query(query, parameters)

            return True, '{} has been updated successfully.'.format(final_name)
        
        except sqlite3.IntegrityError:
            return False, 'Error: Name {} already exists.'.format(final_name)
        

    # Clean table function. This function clean the GUI interface to keep updated the table when we see it. Important: It doesnt clean the table in the database, just clean in the GUI interface.
    # def clean_table(self):
    #     records = self.tree.get_children()
        
    #     for element in records:
    #         self.tree.delete(element)

    # Item selected function
    # def item_selected(self, event):
    #     print(self.tree.item(self.tree.selection())['text'],self.tree.item(self.tree.selection())['values'])
    #     self.message['text'] = 'Selected {}'.format(self.tree.item(self.tree.selection()))

        
    