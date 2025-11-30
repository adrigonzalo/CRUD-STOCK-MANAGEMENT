"""
In this script just include code related with SQLlite
"""
import sqlite3  
import os

class DatabaseManager:

    # Constructor
    def __init__(self, db_path):
        self.db_path = db_path

        self.check_db_folder()
        self.initialize_db()
    
    # Check db connection
    def check_db_folder(self):

        # Check the 'db' folder exists
        folder = os.path.dirname(self.db_path)
        if not os.path.exists(folder):
            os.makedirs(folder) # If the db not exists, create it

    # Run query function
    def run_query(self, query, parameters=()):

        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            result = cursor.execute(query, parameters)
            conn.commit()
        return result
    

    # Initialize db
    def initialize_db(self):

        # Create all the table, if not exists, when the database initialize.
        sql_products = '''
            CREATE TABLE IF NOT EXISTS products (
                "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                "name" TEXT NOT NULL UNIQUE,
                "price" REAL NOT NULL,
                "stock" INTEGER DEFAULT 0,
                "description" TEXT,
                "category_id" INTEGER,
                "supplier_id" INTEGER,
                FOREIGN KEY(category_id) REFERENCES categories(id),
                FOREIGN KEY(supplier_id) REFERENCES suppliers(id)
                )
            '''
        sql_categories = '''
            CREATE TABLE IF NOT EXISTS categories (
                "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                "name" TEXT NOT NULL UNIQUE
                )
            '''
        sql_suppliers = '''
            CREATE TABLE IF NOT EXISTS suppliers (
                "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                "name" TEXT NOT NULL,
                "phone" TEXT
                )
            '''
        
        sql_clients = """
            CREATE TABLE IF NOT EXISTS clients (
                "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                "name" TEXT NOT NULL,
                "email" TEXT,
                "notes" TEXT
                )
        """

        sql_sales = """
            CREATE TABLE IF NOT EXISTS sales (
                "id" INTEGER PRIMARY KEY AUTOINCREMENT,
                "product_id" INTEGER,
                "client_id" INTEGER,
                "quantity" INTEGER NOT NULL,
                "total_price" REAL NOT NULL,
                "payment_method" TEXT,
                "date" TIMESTMAP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(product_id) REFERENCES products(id),
                FOREIGN KEY(client_id) REFERENCES clients(id)                
                )
        """
        
        self.run_query(sql_categories)
        self.run_query(sql_products)
        self.run_query(sql_suppliers)
        self.run_query(sql_clients)
        self.run_query(sql_sales)

        # DEFAULT DATA.
        # Insert a 'General' categorie and supplier to prevent errors when creating products without specifying this data yet.
        try:
            self.run_query('INSERT INTO categories (id, name) VALUES (1, "General")')
            self.run_query('INSERT INTO suppliers (id, name) VALUES (1, "Proveedor Local")')
            self.run_query('INSERT INTO clients (id, name, email) VALUES (1, "Cliente Modelo", "cliente@correo.com")')
        except sqlite3.IntegrityError:
            pass

    # Get products function. Return all the products
    def get_products_db(self):

        query = 'SELECT * FROM products ORDER BY name DESC'
        return self.run_query(query)

    # Search product function. Search products by name
    def search_product_db(self, search_term):

        query = 'SELECT * FROM products WHERE name = ?'
        parameters = ('{}'.format(search_term),) 
        return self.run_query(query, parameters)

    # Insert product function. Insert a new product
    def insert_product_db(self, name, price, stock, category_id):

        query = 'INSERT INTO products VALUES(NULL, ?, ?, ?, "No description", ?, 1)'
        parameters = (name, price, stock, category_id)
        self.run_query(query, parameters)

    # Delete product function. Delete a product by name
    def delete_product_db(self, name):

        query = 'DELETE FROM products WHERE name = ?'
        self.run_query(query, (name,))
        
    # Update an existint product function. Update an existing product by name and price.
    def update_product_db(self, new_name, new_price, old_name):

        query = 'UPDATE products SET name = ?, price = ? WHERE name = ?'
        parameters = (new_name, new_price, old_name) 
        self.run_query(query, parameters)

# -- CATEGORIES -- 
        
    # Get category function. Get the category id by name.
    def get_category_id_by_name_db(self, category_name):

        query_cat = 'SELECT id FROM categories WHERE name = ?'
        return self.run_query(query_cat, (category_name,))
    
    # Get categories function. Return all the categories with the ID and name
    def get_categories_db(self):
        query = 'SELECT id, name FROM categories ORDER BY name ASC'
        return self.run_query(query)
    
    # Insert new category function
    def insert_category_db(self, name):
        query = 'INSERT INTO categories (name) VALUES (?)'
        self.run_query(query, (name,))

    # Delete category function. Delete an existing category by name. Return the cursor if anything was deleted.
    def delete_category_db(self, name):
        query = 'DELETE FROM categories WHERE name = ?'
        return self.run_query(query, (name,))
    

# -- SUPPLIERS --
    # Get suppliers function. Return all the suppliers
    def get_suppliers_db(self):
        query = 'SELECT * FROM suppliers ORDER BY name ASC'
        return self.run_query(query)
    
    # Insert new supplier function
    def insert_supplier_db(self, name, phone):
        query = 'INSERT INTO suppliers (name, phone) VALUES (?, ?)'
        self.run_query(query, (name, phone))

    # Delete suppliers function. Delete an existing supplier by name. Return the cursor if anything was deleted.
    def delete_supplier_db(self, name):
        query = 'DELETE FROM suppliers WHERE name = ?'
        return self.run_query(query, (name,))
    

# -- CLIENTS --
    # Get clients function. Return all the clients
    def get_clients_db(self):
        query = 'SELECT * FROM clients ORDER BY name ASC'
        return self.run_query(query)
    
    # Insert new client function
    def insert_client_db(self, name, email, notes):
        query = 'INSERT INTO clients (name, email, notes) VALUES (?, ?, ?)'
        self.run_query(query, (name, email, notes))

    # Delete client function. Delete an existing client by name. Return the cursor if anything was deleted.
    def delete_client_db(self, name):
        query = 'DELETE FROM clients WHERE name = ?'
        return self.run_query(query, (name,))
    

# -- SALES --
    # Get sales function. Return all the sales
    def get_sales_report_db(self):
        query = '''
            SELECT s.id, p.name, c.name, s.quantity, s.total_price, s.date
            FROM sales s
            JOIN products p ON s.product_id = p.id
            JOIN clients c ON s.client_id = c.id
            ORDER BY s.date DESC
            '''
        return self.run_query(query)
    
    # Insert new sales function
    def insert_sales_db(self, product_id, client_id, quantity, total, method):
        query = 'INSERT INTO sales (product_id, client_id, quantity, total_price, payment_method) VALUES (?, ?, ?, ?, ?)'
        self.run_query(query, (product_id, client_id, quantity, total, method))


    # Update product stock function
    def update_product_stock_db(self, id, stock):
        query = 'UPDATE products SET stock = ? WHERE id = ?'
        return self.run_query(query,(stock, id))