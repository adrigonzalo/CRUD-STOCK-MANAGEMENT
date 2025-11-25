
# LIBRARIES
from tkinter import ttk
from tkinter import *
from tkinter import messagebox
import os
import errno
import sqlite3

# MODULE IMPORTS
from modules.database_manager import DatabaseManager
from modules.product_logic import ProductLogic
from modules.ui_components import ProductForm, ProductTree, SearchForm, CategoryManagerWindow

# PRODUCTS CLASS
class Products:
    
    # Constructor
    def __init__(self, window):
        
        # Create the window interface
        self.wind = window
        self.wind.title('Inventory System')
        
        # --DATABASE CONNECTION--
        
        # Define absolute path

        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, 'db', 'inventory_system.db')

        # Instance manager. This creates autommatically the tables.
        self.db = DatabaseManager(db_path)

        # Use the bussiness logic
        self.logic = ProductLogic(self.db)

        # Styles
        style = ttk.Style()
        style.theme_use('alt')

        # -- MAIN INTERFACE GUI --
        
        # 1. Main Container.
        
        # It is neccesary to use self.logic because the ComboBox need the logic
        self.form = ProductForm(self.wind, self.logic) 
        self.form.grid(
            row = 0,
            column = 0,
            columnspan=3,
            pady= 5,
            padx=5
        )

        # WE DONT NEED TO ADD ALL THE WIDGETS BECAUSE WE HAVE IT IN THE ui_components.py

        # Save Button. The style and the positioning are defined in the ui_components.py
        self.form.save_button.config(command=self.add_product)

        # Output message
        self.message = Label(text='', fg='red')
        self.message.grid(row=1, column=0, columnspan=3, sticky=W + E)

        # 2. Treeview / Table

        self.tree = ProductTree(self.wind)

        # Make interactive table
        self.tree.bind('<<TreeviewSelect>>', self.item_selected)
        self.tree.grid(row=2, column=0, columnspan=3, pady=2, padx=5)

        # Delete and Edit Buttons
        ttk.Button(text='DELETE', command=self.delete_product).grid(row=5, column=0, sticky=W)
        ttk.Button(text='EDIT', command=self.edit_product).grid(row=5, column=1, columnspan=2, sticky=W+E)        
    
        # 3. SEARCH BAR

        self.search_panel = SearchForm(self.wind)
        self.search_panel.grid(row=4, column=0, columnspan=3, pady=10, padx=5, sticky=W+E)

        # Search Button
        self.search_panel.btn_search.config(command=self.search_product)

        # Reset Button to see all again
        self.search_panel.btn_reset.config(command=self.get_products)

        # Load data
        self.get_products()

        # Menubar call
        self.create_menu_bar()

    # -- CONTROLLERS: CONNECTING UI EVENTS TO THE BUSSINESS LOGIC --

    # Search products function
    def search_product(self):

        # Get the text from the SearchForm component
        search_term = self.search_panel.get_search_term()

        # Use the logic with the terms found in the UI
        db_rows = self.logic.search_product(search_term)

        # Clean table
        self.tree.clean_rows()

        # Filling data
        try:
            for row in db_rows:
                self.tree.add_row(row[1],row[2])
        except TypeError as te:
            self.message['text'] = 'No products found matching {}'.format(search_term)

    # Get products function:
    def get_products(self):
        
        # Clean visual table
        self.tree.clean_rows()

        # Ask for the logic data
        db_rows = self.logic.get_products()

        # Fill the table with data using their own method add_rows()
        for row in db_rows:
            self.tree.add_row(name=row[1], price=row[2], stock=row[3], category_id=row[5])
    
    # Add product function
    def add_product(self):

        # Collect data from the Interface
        name, price, stock, category = self.form.get_data()

        # Send data to the logic
        success, message = self.logic.add_product(name, price, stock, category)

        # Update Interface
        self.message['text'] = message

        if success:

            # If it saves well, clean and reload it
            self.form.clear()
            self.get_products()
                
    # Delete product function
    def delete_product(self):

        # Clean verificacion message
        self.message['text'] = ''
        
        # Selected item
        selected_item = self.tree.get_selected_item()

        if not selected_item:
            self.message['text'] = 'Please selected an item.'

            # Adding that, we can make sure that you cant try to delete anything in the database if the selection failed.
            return
            
        # Get name item selected
        name = selected_item[0] # (name, price)
        
        # DELETE CONFIRMATION
        # askyesno return True (Yes) or False (No)

        question = messagebox.askyesno('Confirm Delete','Are you sure you want to delete {}'.format(name))
        
        if question == True:
            
            # Delete Logic 
            success, message = self.logic.delete_product(name)

            # Update UI
            self.message['text'] = message
            if success:
                self.get_products()

        else:
            self.message['text'] = 'Deletion cancelled'


    # Edit product function
    def edit_product(self):

        # Clean verification message
        self.message['text']=''
        
        # Selected item
        selected_item = self.tree.get_selected_item()
        
        if not selected_item:
            self.message['text'] = 'Please selected an item.'

            # Adding that, we can make sure that you cant try to delete anything in the database if the selection failed.
            return
            
        # Get name item selected
        old_name, old_price = selected_item # (name, price)

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
        Button(self.edit_wind, text='Update', command=lambda: self.edit_records(new_name.get(), new_price.get(), old_name, old_price)).grid(row=4, column=0, columnspan=2, sticky=W+E)

        
    # Edit records function
    def edit_records(self, new_name, new_price, old_name, old_price):
        
        # Print records in the terminal before the update
        print(new_name, new_price, old_name)

        # UI logic: If the new values are empty, we need to use the old ones.
        final_name = new_name if new_name else old_name
        final_price = new_price if new_price else old_price

        # Logic Call
        success, message = self.logic.update_product(final_name, final_price, old_name)

        # UI Update
        # Destroy the update window
        self.edit_wind.destroy()
        self.message['text'] = message

        if success:
            self.get_products()

            # Verification message
            self.message['text'] = '{} has been updated successfully.'.format(new_name)

    # Clean table function. This function clean the GUI interface to keep updated the table when we see it. Important: It doesnt clean the table in the database, just clean in the GUI interface.
    def clean_table(self):
        records = self.tree.get_children()
        
        for element in records:
            self.tree.delete(element)

    # Item selected function
    def item_selected(self, event):

        selected = self.tree.get_selected_item()

        if selected:

            self.message['text'] = 'Selected {}'.format(selected[0])

# -- CATEGORIES SECTION --

    # Create the menu bar function
    def create_menu_bar(self):
        
        # Create Menu object
        menubar = Menu(self.wind)
        self.wind.config(menu=menubar)

        # Create the "Management" Menu (Dropdown)
        management_menu = Menu(menubar, tearoff=0)

        # Add options in the "Management" Menu
        management_menu.add_command(label= "Manage Categories", command=self.manage_categories)
        management_menu.add_command(label= "Manage Proveedores", command=self.manage_suppliers)

        # Add a separator
        management_menu.add_separator()
        management_menu.add_command(label='Exit', command=self.wind.quit)

        # Add the drop-down menu to the main bar 
        menubar.add_cascade(label='Gestion', menu=management_menu)
        menubar.add_command(label='Help', command=lambda: messagebox.showinfo("Help", "Inventory System"))

    # Manage categories
    def manage_categories(self):
        """Category managemente menu Handler."""

        # Avoid open multiple managemente windows
        if hasattr(self, 'category_wind') and self.cat_window.winfo_exists():
            self.cat_window.focus()
            return
        
        # -- UI Components

        # 1. Create the window using the UI component
        self.cat_window = CategoryManagerWindow(self.wind)

        # 2. Connect Buttons (Controller -> UI)
        self.cat_window.btn_add.config(command=self.add_category_handler)
        self.cat_window.btn_delete.config(command=self.delete_category_handler)

        # 3. Loading initial data
        self.get_categories_in_window()

        # 4. Calling the main combobox to refreshing it when the windows has been closed.
        self.cat_window.protocol('WM_DELETE_WINDOW', self.close_category_window)


    # Function to close the category window and refresh the combobox in the main form.
    def close_category_window(self):
        self.form.load_categories()
        self.cat_window.destroy()

    
    # Function to load the categories in the Treeview of the managemente window.
    def get_categories_in_window(self):

        # Get the data from the product logic
        db_rows = self.logic.get_all_categories()

        # Filling Treeview with data
        self.cat_window.load_tree_data(db_rows)

    
    # Function to manage the event of add a new category
    def add_category_handler(self):

        name = self.cat_window.get_name_input()

        # Call the logic from procut_logic.py
        success, message = self.logic.add_category(name)

        # Update UI

        # Message info
        self.cat_window.set_message(message)

        if success:
            self.cat_window.clear_input()
            self.get_categories_in_window()

    
    #  Function to manage the event of delete a category
    def delete_category_handler(self):

        self.cat_window.set_message(message) = ''

        name = self.cat_window.get_selected_category_name()

        if not name:
            self.cat_window.set_message('Please select a category', 'red')
            return
        
        # Delete Confirmation
        if messagebox.askyesno('Delete Confirmation', 'Are you sure do you want to delete the category {}?'.format(name)):

            # Call the logic from procut_logic.py
            success, message = self.logic.delete_category(name)

            # Update UI
            self.cat_window.set_message(message)

            if success:
                self.get_categories_in_window()

    def manage_suppliers(self):
        """Handler para el menú de gestión de proveedores."""
        # Crearemos aquí la lógica para abrir la ventana Toplevel
        messagebox.showinfo("Gestión de Proveedores", "Ventana de gestión de proveedores en desarrollo...")

# Main Execution Block
if __name__ == '__main__':
    window = Tk()
    application = Products(window)
    window.mainloop()