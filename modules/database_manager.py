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
        
        self.run_query(sql_categories)
        self.run_query(sql_products)
        self.run_query(sql_suppliers)

        # DEFAULT DATA.
        # Insert a 'General' categorie and supplier to prevent errors when creating products without specifying this data yet.
        try:
            self.run_query('INSERT INTO categories (id, name) VALUES (1, "General")')
            self.run_query('INSERT INTO suppliers (id, name) VALUES (1, "Proveedor Local")')
        except sqlite3.IntegrityError:
            pass