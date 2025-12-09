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

        # Instead of use the query, we call the function in database manager with the self.db
        return self.db.search_product_db(search_term)
    
    # Get products function:
    def get_products(self):

        return self.db.get_products_db()
    
    # Get categories function
    def get_categories(self):

        db_rows = self.db.get_categories_db()

        # For loop to get all the categories
        try:
            categories = []
            for row in db_rows:
                categories.append(row[1])
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
        res_cat = self.db.get_category_id_by_name_db(category_name)
        
        try:

            row = res_cat.fetchone()
            category_id = row[0] if row else 1 # Use ID 1 if it doesnt find anything

        except Exception:
            category_id = 1

        # 4. Query
        try:

            # Execute insert_product_db from database_manager script
            self.db.insert_product_db(name_normalized, price, stock, category_id)
            return True, 'Product {} added successfully.'.format(name_normalized)

        except sqlite3.IntegrityError:
            
            return False, 'Product {} already exists (Database Error).'.format(name_normalized)
                
    # Delete product function
    def delete_product(self, name):
        try:

            # Execute delete_product_db function from the database manager script
            self.db.delete_product_db(name)

            return True, '{} had been deleted successfully.'.format(name)
        
        except Exception as e:

            # Adding that, we can make sure that you cant try to delete anything in the database if the selection failed.
            return False, '{} doesnt exists.'.format(name)

    # Edit product function
    def update_product(self, new_name, new_price, old_name):
        
        try:
            # New Name
            final_name = new_name.capitalize()

            # Execute update_product_db function
            self.db.update_product_db(final_name, new_price, old_name)

            return True, f'{final_name} has been updated successfully.'
        
        except sqlite3.IntegrityError:
            return False, 'Error: Name {} already exists.'.format(final_name)


    # Function to manually update stock
    def manual_update_stock(self, product_name, new_stock):

        # 1. Validation
        try:
            new_stock = int(new_stock)
            
            if new_stock < 0:
                return False, 'Stock quantity cannot be negative.'
            
        except ValueError:

            return False, 'Stock must be a valid integer number.'
        
        # 2. Get Product ID
        res = self.db.search_product_db(product_name)
        product = res.fetchone()

        if not product:
            return False, 'Product not found.'

        prod_id = product[0] 

        # 3. Update stock in DB
        try:
            self.db.update_product_stock_db(prod_id, new_stock)
            return True, f'Stock for product "{product_name}" successfully updated to {new_stock}.'
        
        except Exception as e:

            return False, f'Error updating stock: {e}'
    

    # Function to filter the products depends of the search.
    def filter_products(self, category_name, only_active):

        # Case 1: If exists the selected category (which is not 'All')
        if category_name and category_name != 'All':

            # Get the Category_ID
            res = self.db.get_category_id_by_name_db(category_name)
            cat_data = res.fetchone()

            if cat_data:

                cat_id = cat_data[0]

                # If we want only active too
                if only_active:
                    
                    return self.db.get_active_products_by_category_db(cat_id)
                
                else:

                    return self.db.get_products_by_category_db(cat_id)
                
        
        # Case 2: Without any specific category (All the categories)
        else:
            
            if only_active:

                return self.db.get_active_products_db()
            
            else:

                return self.db.get_products_db() # Return everything

    # -- CATEGORIES -- 
    # Get all categories function
    def get_all_categories(self):
        return self.db.get_categories_db()
    

    # Add category function
    def add_category(self, name):
        
        # Add a new category with some validation
        if not name or name.strip() == '':
            return False, 'The category name cant be empty.'
        
        normalized_name = name.strip().capitalize()

        try:
            self.db.insert_category_db(normalized_name)
            return True, 'Category {} added successfully.'.format(normalized_name)     

        except sqlite3.IntegrityError:
            return False, "Category {} already exists.".format(normalized_name)

        except Exception as e:
            return False, f"Unexpected error occurred: {e}"
        
    # Delete category function
    def delete_category(self, name):
        
        # Delete a category by name using some validation
        if name == 'General':
            return False, "You cant delete the default category 'General'."
        
        try:

            # Calling the delete_category_db function from database manager script. It gives the cursor
            cursor = self.db.delete_category_db(name)

            if cursor.rowcount == 0:
                return False, 'Category {} not found.'.format(name)
        
            else:
                return True, 'Category {} deleted correctly.'.format(name)
        except Exception as e:
            return False, 'Error trying to delete the category: {}'.format(e)
        
    # -- SUPPLIERS -- 
    # Get all suppliers function
    def get_all_suppliers(self):
        return self.db.get_suppliers_db()
    

    # Add supplier function
    def add_supplier(self, name, phone):
        
        # Add a new supplier with some validation
        if not name or name.strip() == '':

            return False, 'The supplier name cant be empty.'
        
        elif not phone or phone.strip() == '':
        
            return False, 'The supplier phone cant be empty.'
        
        normalized_name = name.strip().capitalize()

        try:
            self.db.insert_supplier_db(normalized_name, phone)
            return True, 'Supplier {} added successfully.'.format(normalized_name)     

        except sqlite3.IntegrityError:
            return False, "Supplier {} already exists.".format(normalized_name)

        except Exception as e:
            return False, f"Unexpected error occurred: {e}"
        
    # Delete supplier function
    def delete_supplier(self, name):
        
        # Delete a supplier by name using some validation
        if name == 'Proveedor Local':
            return False, "You cant delete the default supplier 'Proveedor Local'."
        
        try:

            # Calling the delete_supplier_db function from database manager script. It gives the cursor
            cursor = self.db.delete_supplier_db(name)

            if cursor.rowcount == 0:
                return False, 'Supplier {} not found.'.format(name)
        
            else:
                return True, 'Supplier {} deleted correctly.'.format(name)
        except Exception as e:
            return False, 'Error trying to delete the supplier: {}'.format(e)
        

    # -- SALES --

    # Process a sales function. 
    """
    Process a complete sale:
    1- Look for the product and clients IDs.
    2- Check stock
    3- Calculate the discounted price.
    4- Save a sale and subtract stock

    """

    def process_sale(self, product_name, client_name, quantity, discount_percent, payment_method):
        try:

            # 1. Get the data of the product
            res = self.db.search_product_db(product_name)
            product = res.fetchone()

            if not product:
                return False, "Product not found."
            

            prod_id, prod_price, current_stock = product[0], product[2], product[3]

            # 2. Check Stock
            qty = int(quantity)

            if qty <= 0:
                return False, 'Quantity must be positive.'
            
            if current_stock < qty:
                return False, "Insuficient stock. Only {} available.".format(current_stock)
            

            # 3. Get Client ID. 
            res_client = self.db.get_client_id_by_name_db(client_name)
            client_data = res_client.fetchone()

            # If client doesnt found, take the 1 (Model Client).
            client_id = client_data[0] if client_data else 1
            

            # 4. Calculate the total.
            total = prod_price * qty
            final_total = total * (1 - (discount_percent / 100))

            # 5. Transaction (Insert a sale + Update stock)
            self.db.insert_sales_db(prod_id, client_id, qty, final_total, payment_method)

            new_stock = current_stock - qty
            self.db.update_product_stock_db(prod_id, new_stock)

            return True, f"Sale successful! Total: ${final_total:.2f}"
        
        except Exception as e:
            return False, f"Error processing sale: {e}"
        
    # Function to get sales grouped by category
    def get_sales_by_category(self):
        return self.db.get_sales_by_category_db()
    
    # Function to get the sales report
    def get_sales_report(self):

        return self.db.get_sales_report_db().fetchall()
    

    # -- CLIENTS LOGIC --

    # Get all clients
    def get_all_clients(self):
        return self.db.get_clients_db().fetchall()
    
    # Add client
    def add_client(self, name, email, notes):
        
        if not name or not email:
            return False, 'Name and Email are required fields.'
        
        # Email format check
        if '@' not in email or '.' not in email:
            return False, 'Invalid email format.'
        

        # Insert a new client
        try:
            self.db.insert_client_db(name, email, notes)
            return True, f'Client "{name}" added successfully.'
        
        except Exception as e:

            # Check for unique name constraint
            if 'UNIQUE constraint failed' in str(e):
                return False, f'Error: Cliente with name "{name}" already exists.'
            
            return False, f'An error ocurred: {e}'
        
    
    # Delete client
    def delete_client(self, name):

        if not name:
            return False, 'Client name is required for deletion.'
        

        cursor = self.db.delete_client_db(name)

        if cursor.rowcount == 0:
            return False, f'Client "{name}" not found.'
        
        return True, f'Client "{name}" deleted successfully.'