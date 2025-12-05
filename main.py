
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
from modules.ui_components import ProductForm, ProductTree, SearchForm, CategoryManagerWindow, SupplierManagerWindow, SalesPanel, DashboardPanel, ClientManagerWindow, SalesReportWindow

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


        # -- PANEDWINDOW WIDGET --
        self.paned_window = ttk.Panedwindow(self.wind, orient=HORIZONTAL)
        self.paned_window.pack(fill=BOTH, expand=True)


        # Left Panel (Management)
        left_frame = Frame(self.paned_window)
        self.paned_window.add(left_frame, weight=0)

        # Right Panel (Sales and Dashboard)
        right_frame = Frame(self.paned_window)
        self.paned_window.add(right_frame, weight=1)


        # -- MAIN INTERFACE GUI --
        # -- LEFT PANEL CONTENT

        # 1. REGISTER FORM
        
        # It is neccesary to use self.logic because the ComboBox need the logic.
        # anchor = 'nw': It makes the the width of the form fit to the content. We have removed the fill=X.
        self.form = ProductForm(left_frame, self.logic)
        self.form.pack(anchor='nw', padx=5, pady=5) 

        # Save Button. The style and the positioning are defined in the ui_components.py
        self.form.save_button.config(command=self.add_product)

        # 2. Output message
        self.message = Label(left_frame, text='', fg='red')
        self.message.pack(pady=5)

        # 3. Checkbutton Widget (Filter)
        self.show_active_var = IntVar(value = 1)
        self.check_active = Checkbutton(left_frame, text='Show only active products', variable=self.show_active_var, command=self.get_products)
        self.check_active.pack(pady=5)

        # 4. Treeview / Table
        self.tree = ProductTree(left_frame)
        self.tree.pack(fill=BOTH, expand=True, padx=5, pady=5)

        # Make interactive table
        self.tree.bind('<<TreeviewSelect>>', self.item_selected)

        # 5. Delete and Edit Buttons
        btns_frame = Frame(left_frame)
        btns_frame.pack(fill=X, padx=5, pady=5)

        ttk.Button(btns_frame, text='DELETE', command=self.delete_product).pack(side=LEFT, fill=X, expand=True, padx=2)
        ttk.Button(btns_frame, text='EDIT', command=self.edit_product).pack(side=LEFT, fill=X, expand=True, padx=2)        
    
        # 6. Stock Adjustment Widget
        self.stock_frame = LabelFrame(left_frame, text='Adjust Stock')
        self.stock_frame.pack(anchor='nw', padx=5, pady=5)

        Label(self.stock_frame, text='New Stock:').grid(row=0, column=0, padx=5, pady=5)
        self.stock_spinbox = Spinbox(self.stock_frame, from_=0, to=99999, width=10)
        self.stock_spinbox.grid(row=0, column=1, padx=5, pady=5)

        self.btn_update_stock = Button(self.stock_frame, text='Update Stock', command=self.update_stock_handler)
        self.btn_update_stock.grid(row=0, column=2, padx=5, pady=5)

        self.stock_msg = Label(self.stock_frame, text='', fg='black')
        self.stock_msg.grid(row=1, columnspan=3, pady=5)

        # 7. SEARCH BAR

        self.search_panel = SearchForm(left_frame)
        self.search_panel.pack(anchor=W, padx=5, pady=10)

        # Search Button
        self.search_panel.btn_search.config(command=self.search_product)

        # Reset Button to see all again
        self.search_panel.btn_reset.config(command=self.get_products)

        
        # -- RIGHT PANEL CONTENT --

        # 1. Sales Panel.
        # anchor = 'nw': It makes the the width of the form fit to the content. We have removed the fill=X.
        self.sales_panel = SalesPanel(right_frame, self.logic)
        self.sales_panel.pack(anchor='nw', padx=5, pady=5)

        # Connect the 'Confirm Sale' Button to procces the sale
        self.sales_panel.btn_sell.config(command=self.process_sale)

        # Load products at the beginning.
        self.refresh_sales_products()

        # Load clients at the beginning.
        self.refresh_sales_clients()

        # 2. Dashboard
        self.dashboard = DashboardPanel(right_frame)
        self.dashboard.pack(fill=BOTH, expand=True, padx=5, pady=5)

        
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

            category_id = row[5] if len(row) > 5 else 1
            self.tree.add_row(name=row[1], price=row[2], stock=row[3], category_id=category_id)
    
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

            # Reload the sales dropdown to add a product
            self.refresh_sales_products()
                
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
        old_name = selected_item[0] # name
        old_price = selected_item[1] # price

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
            self.message['text'] = '{} has been updated successfully.'.format(final_name)
        else:
            self.message['text'] = message

    # Procces a product sales function. It is not the same as the procces_sale function in product_logic.py
    def process_sale(self):

        # 1. Get the data from the sales panel
        sale_data = self.sales_panel.get_sale_data()

        product_name = sale_data['product_name']
        quantity = sale_data['quantity']
        discount = sale_data['discount']
        payment_method = sale_data['payment_method']
        client_name = sale_data['client_name']

        # 2. Validation to make sure that we dont confirm a default sale
        if product_name == 'Select product...' or product_name == 'No products available.':
            self.sales_panel.set_message('Please select a valid product','red')
            return


        # 3. Process sale through logic
        success, message = self.logic.process_sale(
            product_name=product_name,
            client_name=client_name, 
            quantity=quantity,
            discount_percent=discount,
            payment_method=payment_method
        )

        # 4. Update UI.
        if success:
            self.sales_panel.set_message(message, 'green')
            
            self.get_products()

            self.sales_panel.reset_form()
            
            # Update the Dashboard
            self.update_dashboard()
        
        else:
            self.sales_panel.set_message(message, 'red')

        # Add the log 
        self.dashboard.add_log(f'Sale: {product_name} x{quantity} - {message}')
    
    
    # Function to refresh products in Sales Panel OptionMenu
    def refresh_sales_products(self):

        # 1. Get all the products from the logic layer
        products_data = self.logic.get_products().fetchall()

        # 2. Extract only the names
        product_names = [row[1] for row in products_data]

        # 3. Pass the lista of names to the SalesPanel component
        self.sales_panel.load_products(product_names)


    # Function to create a handler for manually updating product stock
    def update_stock_handler(self):

        # 1. Clear previous message
        self.stock_msg.config(text='', fg='black')

        # 2. Get selected product name
        item_id = self.tree.focus()
        
        if not item_id:
            self.stock_msg.config(text='Please select a product first.', fg='red')
            return
        
        product_name = self.tree.item(item_id, 'text') # Product name is the first column

        # 3. Get the new stock value
        new_stock = self.stock_spinbox.get()

        # 4. Confirmation
        if not messagebox.askyesno('Confirm stock update',f'Are you sure you want to change the stock for "{product_name}" to {new_stock}?'):

            return
        
        # 5. Call Logic
        success, message = self.logic.manual_update_stock(product_name, new_stock)

        # 6. Update UI feedback and table
        self.stock_msg.config(text=message, fg='green' if success else 'red')

        if success:

            self.get_products()
            self.refresh_sales_products() # It is optional but i added it to update the sales panel
            self.stock_spinbox.delete(0, END)
            self.stock_spinbox.insert(0, 0)




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
        reports_menu = Menu(menubar, tearoff=0)

        # Add options in the "Management" Menu
        management_menu.add_command(label= "Manage Categories", command=self.manage_categories)
        management_menu.add_command(label= "Manage Suppliers", command=self.manage_suppliers)
        management_menu.add_command(label= "Manage Clients", command=self.manage_clients)

        # Add a separator
        management_menu.add_separator()
        management_menu.add_command(label='Exit', command=self.wind.quit)

        # Add the drop-down menu to the main bar 
        menubar.add_cascade(label='Management', menu=management_menu)
        
        reports_menu.add_command(label='Sales History', command=self.open_sales_report)
        menubar.add_cascade(label='Reports', menu=reports_menu)

        menubar.add_command(label='Help', command=lambda: messagebox.showinfo("Help", "Inventory System"))

    # Manage categories
    def manage_categories(self):
        """Category management menu Handler."""

        # Avoid open multiple management windows
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

        self.cat_window.set_message('')

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

    # Manage suppliers
    def manage_suppliers(self):
        """Suppliers management menu Handler."""

        # Avoid open multiple management windows
        if hasattr(self, 'supp_wind') and self.supp_window.winfo_exists():
            self.supp_window.focus()
            return
        
        # -- UI Components

        # 1. Create the window using the UI component
        self.supp_window = SupplierManagerWindow(self.wind)

        # 2. Connect Buttons (Controller -> UI)
        self.supp_window.btn_add.config(command=self.add_supplier_handler)
        self.supp_window.btn_delete.config(command=self.delete_supplier_handler)

        # 3. Loading initial data
        self.get_suppliers_in_window()

    
    # Function to load the supppliers in the Treeview of the managemente window.
    def get_suppliers_in_window(self):

        # Get the data from the product logic
        db_rows = self.logic.get_all_suppliers()

        # Filling Treeview with data
        self.supp_window.load_tree_data(db_rows)

    
    # Function to manage the event of add a new category
    def add_supplier_handler(self):

        name, phone = self.supp_window.get_inputs()

        # Call the logic from procut_logic.py
        success, message = self.logic.add_supplier(name, phone)

        # Update UI

        # Message info
        self.supp_window.set_message(message)

        if success:
            self.supp_window.clear_inputs()
            self.get_suppliers_in_window()

    
    #  Function to manage the event of delete a supplier
    def delete_supplier_handler(self):

        self.supp_window.set_message('')

        name = self.supp_window.get_selected_supplier_name()

        if not name:
            self.supp_window.set_message('Please select a supplier', 'red')
            return
        
        # Delete Confirmation
        if messagebox.askyesno('Delete Confirmation', 'Are you sure do you want to delete the supplier {}?'.format(name)):

            # Call the logic from procut_logic.py
            success, message = self.logic.delete_supplier(name)

            # Update UI
            self.supp_window.set_message(message)

            if success:
                self.get_suppliers_in_window()
    

    # Function to fetch and update the Dashboard visuals
    def update_dashboard(self):

        # Get sales data from the logic layer
        sales_data = self.logic.get_sales_by_category()

        # Get data to the Dashboard component for drawing
        self.dashboard.draw_sales_graph(sales_data)

    
    # -- CLIENTS -- 
    def manage_clients(self):

        # Create the Cliente Manager Window
        self.client_window = ClientManagerWindow(self.wind)

        # Connect handlers
        self.client_window.add_button.config(command=self.add_client_handler)
        self.client_window.delete_button.config(command=self.delete_client_handler)

        # Load initial data
        self.get_clients_in_window()

    # Function to fetch and load client data into the Treeview
    def get_clients_in_window(self):

        # Call the logic to get all clients
        db_rows = self.logic.get_all_clients()

        # Filling Treeview with data
        self.client_window.load_tree_data(db_rows)

    # Function to manage the event of adding a new client
    def add_client_handler(self):

        # Get the data from the input or texts
        name, email, notes = self.client_window.get_inputs()

        # Call the logic
        success, message = self.logic.add_client(name=name, email=email, notes=notes)

        # Update the UI
        self.client_window.set_message(message, 'green' if success else 'red')

        if success:

            self.client_window.clear_inputs()
            self.get_clients_in_window() # Reload data

            self.refresh_sales_clients()

    # Function to manage the event of deleting a client
    def delete_client_handler(self):

        self.client_window.set_message('')

        name = self.client_window.get_selected_client_name()

        if not name:
            self.client_window.set_message('Please select a client','red')
            return
        
        # Deletion Confirmation
        if messagebox.askyesno('Delete Confirmation', f'Are you sure you want to delete the client {name}?'):

            # Call the logic
            success, message = self.logic.delete_client(name)

            # Update UI
            self.client_window.set_message(message, 'green' if success else 'red')

            if success:
                self.get_clients_in_window() # Reload data
    
    # Function to refresh clients in Sales Panel OptionMenu
    def refresh_sales_clients(self):

        # 1. Get all the clients from the logic layer
        clients_data = self.logic.get_all_clients()

        # 2. Extract only the names
        client_names = [row[1] for row in clients_data]

        # 3. Pass the list of names to the SalesPanel component
        self.sales_panel.load_clients(client_names)

    
    # Function to open Sales Report
    def open_sales_report(self):

        # Create Window
        report_window = SalesReportWindow(self.wind)

        # Get data from Logic
        sales_data = self.logic.get_sales_report()

        # Load data into UI
        report_window.load_data(sales_data)
                                             
# Main Execution Block
if __name__ == '__main__':
    window = Tk()
    application = Products(window)
    window.mainloop()