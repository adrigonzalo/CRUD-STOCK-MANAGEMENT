
# LIBRARIES
from tkinter import ttk
from tkinter import *
import os
import errno
import sqlite3

# PRODUCTS CLASS
class Products:
    
    # Db variable
    db_name = r'.\db\database_products_2.db'

    # Constructor
    def __init__(self, window):
        self.wind = window
        self.wind.title('Prueba de Products Application')

        frame = LabelFrame(self.wind, text = 'Register a new product')
        frame.grid(
            row = 0,
            column = 0,
            columnspan=3,
            pady= 5,
            padx=5
        )

        # Name Input
        Label(frame, text='Name:').grid(row=1, column=0)
        self.name = Entry(frame)
        self.name.focus()
        self.name.grid(row=1, column=1)

        # Price Input
        Label(frame, text='Price:').grid(row=2, column=0)
        self.price = Entry(frame)
        self.price.grid(row=2, column=1, pady=2, padx=5)

        # Button
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

        # Treeview / Table
        height = 10
        self.tree = ttk.Treeview(height=height, columns=2, selectmode=BROWSE)

        # Make interactive table
        self.tree.bind('<<TreeviewSelect>>', self.item_selected)
        self.tree.grid(row=4, column=0, columnspan=3, pady=2, padx=5)

        # Table Headings
        self.tree.heading('#0', text='Name', anchor=CENTER)
        self.tree.heading('#1', text='Price', anchor=CENTER)

        # Buttons
        ttk.Button(text='DELETE', command=self.delete_product).grid(row=5, column=0, sticky=W)
        ttk.Button(text='EDIT', command=self.edit_product).grid(row=5, column=1, columnspan=2, sticky=W+E)        
    
        # Load data
        self.get_products()

    # Get products function:
    def get_products(self):
        self.clean_table()

        query = 'SELECT * FROM products2 ORDER BY name DESC'
        db_rows = self.run_query(query)

        try:
            for row in db_rows:
                self.tree.insert('', 0, text=row[1], values=row[2])
        except TypeError as te:
            self.message['text'] = self.message['text'] + '\nThere is not any products.'

    # Validation function
    def validation(self):
        # Validate if name or price inputs are not empty
        if not self.name.get() or not self.price.get():
            self.message['text'] = 'Name and price inputs are required.'
        
        # Validate if price input has a valid number
        try:
            price_value = float(self.price.get())
        except ValueError as ve:
            print(ve)
            self.message['text'] = 'Price input must be a valid number.'
            return False
        
        # Validate if price input has a positive value
        if price_value <= 0:
            self.message['text'] = "Price input must have a positive value."
            return False
        
        self.message['text'] = ''
        return True 
    
    # Add product function
    def add_product(self):
        if self.validation():
            
            # Query
            query = 'INSERT INTO products2 VALUES(NULL, ?, ?)'

            # Parameters to use the run_query() function
            parameters = (self.name.get(), self.price.get())

            # Execute run_query
            self.run_query(query, parameters)

            # Get products
            self.get_products()

            # Add product verification
            self.message['text'] = 'Product {} added successfully.'.format(self.name.get())

            # Clean Entries
            self.name.delete(0, END)
            self.price.delete(0, END)

    # Delete product function
    def delete_product(self):
        try:

            # Clean verificacion message
            self.message['text'] = ''

            # Making sure the product is selected. 
                # With .tree.item we can query or modify the options for the specified item
                # With .tree.selection return a tuple of selected items.
            self.tree.item(self.tree.selection())['text'][0]

            # Verificaton message
            self.message['text'] = ''

            # Query
            query = 'DELETE FROM products2 WHERE name = ?'

            # Get name item selected
            name = self.tree.item(self.tree.selection())['text']

            # Execute run_query
            self.run_query(query,(name,))

            # Delete product message
            self.message['text'] = '{} has been deleted successfully.'.format(name)

            # Get products
            self.get_products()

        except IndexError as ie:

            print('Error: ', ie)
            self.message['text'] = 'Please selected an item.'

            # Adding that, we can make sure that you cant try to delete anything in the database if the selection failed.
            return

    # Edit product function
    def edit_product(self):
        # Clean verification message
        self.message['text']=''
        
        try:
            # Clean verification message
            self.message['text']=''

            # Making sure the product is selected. 
                # With .tree.item we can query or modify the options for the specified item
                # With .tree.selection return a tuple of selected items.
            self.tree.item(self.tree.selection())['text'][0]


            # Define old_name, old_price variables to get the old value inserted in the table before any change.
                # We use ['text'] after all the code in old_name variable because the key is asociated with the row[1] and, at the same time, with the hide column #0 which is called "Name" in the table.
                # We use ['values'][0] after all the code in old_price variable because it contains all the additional columns which it starts with #1, #2... 
                # row[2] is associated to the values tuple. It has the #1 column values, which it named "Price"
            old_name = self.tree.item(self.tree.selection())['text']        
            old_price = self.tree.item(self.tree.selection())['values'][0]

            # Print old variables.
            print("Old name: ", old_name, "Old_price: ", old_price)

            # Using Tkinter to use an independent window for update a record.
            self.edit_wind = Toplevel()
            self.edit_wind.title = 'Edit Product'

            # Old Name
            Label(self.edit_wind, text='Old Name:').grid(row=0, column=0, padx=10, pady=5)
            Entry(self.edit_wind, textvariable=StringVar(self.edit_wind, value=old_name), state='readonly').grid(row=0, column=1)

            # New Name
            Label(self.edit_wind, text='New Name:').grid(row=1, column=0, padx=10, pady=5)
            new_name = Entry(self.edit_wind)
            new_name.grid(row=1, column=1, padx=10, pady=5)

            # Old Price
            Label(self.edit_wind, text='Old Price:').grid(row=2, column=0, padx=10, pady=5)
            Entry(self.edit_wind, textvariable=StringVar(self.edit_wind, value=old_price), state='readonly').grid(row=2, column=1)

            # New Price
            Label(self.edit_wind, text='New Price:').grid(row=3, column=0, padx=10, pady=5)
            new_price = Entry(self.edit_wind)
            new_price.grid(row=3, column=1, padx=10, pady=5)

            # Update Button
            Button(self.edit_wind, text='Update', command=lambda: self.edit_records(new_name.get(), new_price.get(), old_name)).grid(row=4, column=0, columnspan=2, sticky=W+E)

        except IndexError as ie:
            self.message['text'] = 'Please select a record'
            return
        
    # Edit records function
    def edit_records(self, new_name, new_price, old_name):
        
        # Print records in the terminal before the update
        print(new_name, new_price, old_name)

        # Update query
        query = 'UPDATE products2 SET name = ?, price = ? WHERE name = ?'

        # Parameters to the run_query function
        parameters = (new_name, new_price, old_name)

        # Execute run_query 
        self.run_query(query, parameters)

        # Destroy the update window
        self.edit_wind.destroy()

        # Verification message
        self.message['text'] = '{} has been updated successfully.'.format(new_name)

        # Get products
        self.get_products()

    # Run query function
    def run_query(self, query, parameters=()):
        self.message['text']=''

        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                result = cursor.execute(query, parameters)
                conn.commit()
            return result
        except sqlite3.Error as error:
            print(error)
            self.create_db()

    # Clean db function
    def clean_table(self):
        records = self.tree.get_children()
        
        for element in records:
            self.tree.delete(element)
    
    # Create database function
    def create_db(self):
        self.message['text']=''

        try:
            os.mkdir('db')
        except OSError as ose:
            print('The directory already exists.')
            if ose.errno != errno.EEXIST:
                raise
        
        # Connect to the db
        conn = sqlite3.connect(self.db_name)
        c = conn.cursor()
        c.execute('''
        CREATE TABLE "products2" (
                  "id" INTEGER NOT NULL UNIQUE,
                  "name" TEXT NOT NULL,
                  "price" REAL NOT NULL,
                  PRIMARY KEY("id" AUTOINCREMENT)
                  )
        ''')
        self.message['text']='The table {} has been created successfully'.format(self.tree)
        conn.commit()

    # Item selected function
    def item_selected(self, event):
        print(self.tree.item(self.tree.selection())['text'],self.tree.item(self.tree.selection())['values'])
        self.message['text'] = 'Selected {}'.format(self.tree.item(self.tree.selection()))


# Main Execution Block
if __name__ == '__main__':
    window = Tk()
    application = Products(window)
    window.mainloop()