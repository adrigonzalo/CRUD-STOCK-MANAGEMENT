
"""
---- GESTION DE INVENTARIO CON CRUD ----

En este proyecto vamos a trabajar para crear una GESTION DE INVENTARIO utilizando CRUD (Create Read Update Delete).
Para ello se van a utilizar las siguientes librerias:

- tkinter: Libreria que nos permite trabajar con la interfaz de GUI de Python.
- os: Libreria que nos permite movernos por el sistema operativo para realizar distintas operaciones.
- errno: Libreria que nos permite capturar errores de codigo con un sistma estandar de simbolos
- sqlite3: Libreria que nos permite trabajar con consultas SQL y que viene integrada con el paquete de Python.

"""
# LIBRARIES
from tkinter import ttk
from tkinter import *
import os
import errno
import sqlite3

# PRODUCTS CLASS   
class Products:
    
    # Database variable.
    db_name = r'.\db\database_products.db'

    # Constructor
    def __init__(self, window):
        self.wind = window
        self.wind.title('Products Application')

        # Creating a frame container
        frame = LabelFrame(self.wind, text = 'Register a new Product')
        frame.grid(
            row = 0,
            column = 0,
            columnspan=3,
            pady= 5,
            padx=5
        )

        # Name Input
        Label(frame, text='Name: ').grid(row=1, column=0)
        self.name = Entry(frame) # Where you can write a text
        self.name.focus() # .focus() pinpoint the Name Input
        self.name.grid(row=1, column=1)

        # Price Input
        Label(frame, text='Price: ').grid(row=2, column=0)
        self.price = Entry(frame) # Where you can write a text
        self.price.grid(row=2, column=1, pady=2, padx=5) 

        # Button to add a product
        ttk.Button(
            frame,
            text='Save Product',
            command=self.add_product
        ).grid(
            row=3, 
            columnspan=3, 
            sticky=W+E, 
            pady=2, 
            padx=5
            )    

        # Output message
        self.message = Label(text='', fg='red')
        self.message.grid(row=3, column=0, columnspan=3, sticky=W + E)

        # Treeview /  Table
        height = 10
        self.tree = ttk.Treeview(height=height, columns=2, selectmode=BROWSE) # Define the table
        
        # Making the table interactive.
            # .bind(): This Tkinter method is used to associate a specific widget event (self.tree) with a method which should executed when the event happends.
            # <<TreeviewSelect>>: This is a event string defined by Tkinter for the widget Treeview. It means like "It has selected a table item"
        self.tree.bind("<<TreeviewSelect>>", self.item_selected)    
        self.tree.grid(row=4, column=0, columnspan=3, pady=2, padx=5)

        # Headings table
        self.tree.heading('#0', text='Name', anchor=CENTER)
        self.tree.heading('#1', text='Price', anchor=CENTER)        

        # Buttons
        ttk.Button(text='DELETE', command=self.delete_product).grid(row=5, column=0, sticky=W)
        ttk.Button(text='EDIT', command=self.edit_product).grid(row=5, column=1, columnspan=2, sticky=W+E)        
    
        # Load data
        self.get_products()

    # Run query function
    def run_query(self, query, parameters=()):
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                result = cursor.execute(query, parameters)
                conn.commit()
            return result
        except sqlite3.Error as error:
            print(error)
            self.create_db()

    # Get products function
    def get_products(self):

        # Clean table
        self.clean_table()

        # Quering data with a SELECT
        query = 'SELECT * FROM products ORDER BY name DESC'
        db_rows = self.run_query(query)

        # Filling data
        try:
            for row in db_rows:
                self.tree.insert('', 0, text=row[1], values=row[2])
        
        except TypeError as te:
            self.message['text'] = self.message['text'] + "\There isn't any product."

    # Validatiom function.
    def validation(self):
        
        # Validate if input entries are not empty
        if not self.name.get() or not self.price.get():
            self.message['text'] = 'Name and price are required.'
            return False
        
        # Validate price field is a valid number
        try:
            price_value = float(self.price.get())

        except ValueError as ve:
            self.message['text'] = 'Price must be a valid number.'
            return False
        
        # Validate price is a positive number
        if price_value <=0:
            self.message['text'] = 'Price must be greater than zero.'
            return False
        
        # If all the validations are correct
        self.message['text'] = ''
        return True
    
    # Clean table function
    def clean_db(self):
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)

    # Add product
    def add_product(self):
        if self.validation():
           # SQL query
           query = 'INSERT INTO products VALUES(NULL, ?, ?)'

           # Get the parameters
           parameters = (self.name.get(), self.price.get())

           # Executhe the query
           self.run_query(query, parameters)

           # Get the products
           self.get_products()

           # Products add verification
           self.message['text'] = 'Product {} added successfully'.format(self.name.get())

           # Cleean the Name and Price Entry
           self.name.delete(0, END)
           self.price.delete(0, END)

    def delete_product(self):
        self.message['text'] = ''
        try:
            # Me aseguro que he seleccionado un registro
            self.tree.item(self.tree.selection())['text'][0]

            self.message['text'] = ''
            name = self.tree.item(self.tree.selection())['text']
            query = 'DELETE FROM products WHERE name = ?'
            self.run_query(query, (name,))
            self.message['text'] = 'Record "{}" deleted successfully'.format(name)
            self.get_products()
        except IndexError as e:
            print("error:", e)
            self.message['text'] = 'Please select a record'
            
            # Adding that, we can make sure that you cant try to delete anything in the database if the selection failed.
            return

    def edit_product(self):
        self.message['text'] = ''
        try:
            # Me aseguro que he seleccionado un registro
            self.tree.item(self.tree.selection())['text'][0]

            name = self.tree.item(self.tree.selection())['text']
            old_price = self.tree.item(self.tree.selection())['values'][0]
            print(f"name: {name} / price: {old_price}")

            # self.edit_wind = edit_wind is a variable that is used to represent and editing window, created with the Tkinter library.
            # Toplevel() = Create a new, separate windows that exists independently from the main application window
            self.edit_wind = Toplevel()
            self.edit_wind.title = "Edit Product"

            # Old Name
            Label(self.edit_wind, text="Old Name:").grid(row=0, column=0, padx=10, pady=5)
            Entry(self.edit_wind, textvariable=StringVar(self.edit_wind, value=name), state='readonly') \
                .grid(row=0, column=1)
            # New Name
            Label(self.edit_wind, text='New Name').grid(row=1, column=0, padx=10, pady=5)
            new_name = Entry(self.edit_wind)
            new_name.grid(row=1, column=1, padx=10, pady=5)
            # Old Price
            Label(self.edit_wind, text="Old Price:").grid(row=2, column=0, padx=10, pady=5)
            Entry(self.edit_wind, textvariable=StringVar(self.edit_wind, value=old_price), state='readonly') \
                .grid(row=2, column=1)
            # New Price
            Label(self.edit_wind, text='New Price').grid(row=3, column=0, padx=10, pady=5)
            new_price = Entry(self.edit_wind)
            new_price.grid(row=3, column=1, padx=10, pady=5)
            # Button
            Button(self.edit_wind, text='Update',
                   command=lambda: self.edit_records(new_name.get(), new_price.get(), name)) \
                .grid(row=4, column=0, columnspan=2, sticky=W+E)

        except IndexError as e:
            self.message['text'] = 'Please select a record'
            return

    def edit_records(self, new_name, new_price, old_name):
        print(new_name, new_price, old_name)
        query = 'UPDATE products SET name = ?, price = ? WHERE name = ?'
        parameters = (new_name, new_price, old_name)
        self.run_query(query, parameters)
        self.edit_wind.destroy()
        self.message['text'] = 'Record {} updated successfully'.format(new_name)
        self.get_products()

    # Clean table
    def clean_table(self):
        records = self.tree.get_children()
        for element in records:
            self.tree.delete(element)
    
    # Create database function
    def create_db(self):

        # Making sure that the db directory exists
        try:
            os.mkdir('db')

        except OSError as e:
            print("The directory already exists.")
            if e.errno != errno.EEXIST:
                raise # Run a manual exception to stop the program execution.
        
        # Connect to the db
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor() # The database with be saved in the location where the 'py' file is save
        c.execute('''
        CREATE TABLE "products" (
                  "id" INTEGER NOT NULL UNIQUE,
                  "name" TEXT NOT NULL,
                  "price" REAL NOT NULL,
                  PRIMARY KEY("id" AUTOINCREMENT)
                  )
        ''')
        self.message['text'] = 'The table has been created successfully.'
        conn.commit()

    # Item selected function
    def item_selected(self, event):
        print(self.tree.item(self.tree.selection())['text'], self.tree.item(self.tree.selection())['values'])
        message = self.tree.item(self.tree.selection())
        self.message['text'] = 'Selected {}'.format(message)

if __name__ == '__main__':
    window = Tk()
    application = Products(window)
    window.mainloop()