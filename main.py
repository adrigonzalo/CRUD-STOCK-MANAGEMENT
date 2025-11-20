
# LIBRARIES
from tkinter import ttk
from tkinter import *
from tkinter import messagebox
import os
import errno
import sqlite3

# MODULE IMPORTS
from modules.database_manager import DatabaseManager

# PRODUCTS CLASS
class Products:
    
    # Constructor
    def __init__(self, window):
        
        # Create the window interface
        self.wind = window
        self.wind.title('Prueba de Products Application')
        
        # --DATABASE CONNECTION--
        
        # Define absolute path

        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, 'db', 'inventory_system.db')

        # Instance manager. This creates autommatically the tables.
        self.db = DatabaseManager(db_path)

        # Styles
        style = ttk.Style()
        style.theme_use('alt')

        # -- MAIN INTERFACE GUI --
        
        # Main Container 
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

        # Save Button
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

        # Adjust width and align
        #self.tree.column('#0', width=200, anchor=CENTER)
        #self.tree.column('#1', width=100, anchor=CENTER)

        # Delete and Edit Buttons
        ttk.Button(text='DELETE', command=self.delete_product).grid(row=5, column=0, sticky=W)
        ttk.Button(text='EDIT', command=self.edit_product).grid(row=5, column=1, columnspan=2, sticky=W+E)        
    
        # SEARCH BAR
        search_frame = LabelFrame(self.wind,text='Search Product')
        search_frame.grid(row=6, column=0, columnspan=3, pady=10, padx=5, sticky=W+E)

        # Search Label and Entry
        Label(search_frame,text='Search by Name:').grid(row=0, column=0, padx=5, pady=5)
        self.search_entry = Entry(search_frame)
        self.search_entry.grid(row=0,column=1, padx=5, pady=5)

        # Search Button
        ttk.Button(search_frame,text='Search', command=self.search_product).grid(row=0, column=2, padx=5, pady=5)

        # Reset Button to see all again
        ttk.Button(search_frame,text='Show all', command=self.get_products).grid(row=0, column=3, padx=5, pady=5)

        # Load data
        self.get_products()

    # -- BUSSINESS LOGIC --

    # Search products function
    def search_product(self):

        # Get the search string
        search_term = self.search_entry.get()

        # Clean verification message
        self.message['text'] = ''

        # Query
        query = 'SELECT * FROM products WHERE name = ?'

        # Parameters
        parameters = ('{}'.format(search_term),)

        # Run_query
        db_rows = self.db.run_query(query, parameters)

        # Clean table
        self.clean_table()

        # Filling data
        try:
            for row in db_rows:
                self.tree.insert('', 0, text=row[1], values=row[2])
        except TypeError as te:
            self.message['text'] = 'No products found matching {}'.format(search_term)

    # Get products function:
    def get_products(self):
        self.clean_table()

        query = 'SELECT * FROM products ORDER BY name DESC'

        db_rows = self.db.run_query(query) # Actually, we need to include db in the instance because we have it in other script

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
            # We insert default values in the new columns until create the widgets
            query = 'INSERT INTO products VALUES(NULL, ?, ?, 0, "No description", 1, 1)'

            # NORMALIZE DATA
            # .capitalize(): Turns 'MaNzaNa' into 'Manzana'

            name_normalized = self.name.get().capitalize()

            # Parameters to use the run_query() function
            parameters = (name_normalized, self.price.get())
            
            try:

                # Execute run_query
                self.db.run_query(query, parameters)

                # Get products
                self.get_products()

                # Add product verification
                self.message['text'] = 'Product {} added successfully.'.format(name_normalized)

                # Clean Entries
                self.name.delete(0, END)
                self.price.delete(0, END)
            except sqlite3.IntegrityError as e:

                # This code only executes if the UNIQUE fails.
                self.message['text'] = 'Product {} already exists (Database Error).'.format(name_normalized)

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
            
            # Get name item selected
            name = self.tree.item(self.tree.selection())['text']
            
            #DELETE CONFIRMATION
            # askyesno return True (Yes) or False (No)

            question = messagebox.askyesno('Confirm Delete','Are you sure you want to delete {}'.format(name))
            
            if question == True:

                # Query
                query = 'DELETE FROM products WHERE name = ?'

                # Execute run_query
                self.db.run_query(query,(name,))

                # Delete product message
                self.message['text'] = '{} has been deleted successfully.'.format(name)

                # Get products
                self.get_products()
            else:
                self.message['text'] = 'Deletion cancelled'

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
        query = 'UPDATE products SET name = ?, price = ? WHERE name = ?'

        # Parameters to the run_query function
        parameters = (new_name, new_price, old_name)

        # Execute run_query 
        self.db.run_query(query, parameters)

        # Destroy the update window
        self.edit_wind.destroy()

        # Verification message
        self.message['text'] = '{} has been updated successfully.'.format(new_name)

        # Get products
        self.get_products()

    # Clean table function. This function clean the GUI interface to keep updated the table when we see it. Important: It doesnt clean the table in the database, just clean in the GUI interface.
    def clean_table(self):
        records = self.tree.get_children()
        
        for element in records:
            self.tree.delete(element)

    # Item selected function
    def item_selected(self, event):
        print(self.tree.item(self.tree.selection())['text'],self.tree.item(self.tree.selection())['values'])
        self.message['text'] = 'Selected {}'.format(self.tree.item(self.tree.selection()))


# Main Execution Block
if __name__ == '__main__':
    window = Tk()
    application = Products(window)
    window.mainloop()