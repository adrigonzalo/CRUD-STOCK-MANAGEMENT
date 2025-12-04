"""
In this script only include code related with specific widget classes like Menus, Forms...
"""

from tkinter import *
from tkinter import ttk

# -- MAIN INTERFACE GUI --
class ProductForm(LabelFrame):

        # Constructor
        def __init__(self, parent, logic_instance, title = 'Register a new product'):
                super().__init__(parent, text=title) 
                self.logic = logic_instance
                self.init_widgets()
                self.load_categories()


        # Initialize widgets
        def init_widgets(self):
                                
            # Name Input
            Label(self, text='Name:').grid(row=1, column=0)
            self.name = Entry(self)
            self.name.focus()
            self.name.grid(row=1, column=1)

            # Price Input
            Label(self, text='Price:').grid(row=2, column=0)
            self.price = Entry(self)
            self.price.grid(row=2, column=1, pady=2, padx=5)

            # Categories Combobox
            Label(self, text='Category:').grid(row=3, column=0)

            self.combo_category = ttk.Combobox(self, state='readonly')
            self.combo_category.grid(row=3, column=1, pady=2, padx=5)

            # Stock Spinbox
            Label(self, text='Stock:').grid(row=4, column=0)

            # from_:0, to=1000 define the range
            self.spinbox = Spinbox(self, from_=0, to=1000)
            self.spinbox.grid(row=4, column=1, pady=2, padx=5)

            # Description Label and Text Area
            Label(self, text='Description:').grid(row=5, column=0, pady=2, padx=5, sticky=W)
            self.description = Text(self, height=3, width=25)
            self.description.grid(row=5, column=1, columnspan=2, pady=2, padx=5, sticky=W+E) 
            
            # Save Button. 
            # We dont add the command arguments yet, because will main.py do
            self.save_button = ttk.Button(self,text='Save Product')
            self.save_button.grid(row=6, columnspan=3, sticky=W+E, pady=2,padx=5)    

            # Output message
            self.message = Label(self, text='', fg='red')
            self.message.grid(row=7, column=0, columnspan=3, sticky=W + E)

        # Load categories
        def load_categories(self):
            categories = self.logic.get_categories()
            self.combo_category['values'] = categories

            if categories:
                  self.combo_category.current(0)

        # Get data. Return a tuple with the current data from the form
        def get_data(self):
            return(self.name.get(),
                   self.price.get(),
                   self.spinbox.get(),
                   self.combo_category.get())
        
        # Clear data from form
        def clear(self):
            self.name.delete(0,END)
            self.price.delete(0,END)
            self.spinbox.delete(0,END)
            self.price.insert(0,0)

            if self.combo_category['values']:
                 self.combo_category.current(0)


class SearchForm(LabelFrame):
    # Constructor
    def __init__(self, parent, title = 'Search Product'):
            super().__init__(parent, text=title) 
            self.init_widgets()

    # Initialize Search widgets
    def init_widgets(self):
        
        # Search Label and Entry
        Label(self, text='Search by Name:').grid(row=0, column=0, padx=5, pady=5)
        self.search_entry = Entry(self)
        self.search_entry.grid(row=0,column=1, padx=5, pady=5)

        # Search Button
        self.btn_search = ttk.Button(self, text='Search')
        self.btn_search.grid(row=0, column=2, padx=5, pady=5)

        # Reset Button to see all again
        self.btn_reset = ttk.Button(self, text='Show all')
        self.btn_reset.grid(row=0, column=3, padx=5, pady=5)

    # Get search term
    def get_search_term(self):
        
        return self.search_entry.get()
    

class ProductTree(ttk.Treeview):

    # Constructor
    def __init__(self, parent):
        super().__init__(parent, height=10, columns=('#1','#2','#3'), selectmode=BROWSE)   
        self.init_config()


    # Initialize configuration
    def init_config(self):

        # Table Headings
        self.heading('#0', text='Name', anchor=CENTER)
        self.heading('#1', text='Price', anchor=CENTER)
        self.heading('#2', text='Stock', anchor=CENTER)
        self.heading('#3', text='Category_ID', anchor=CENTER)

    # Clean visual rows
    def clean_rows(self):

        records = self.get_children()
        for element in records:
             self.delete(element)

    # Add a row
    def add_row(self, name, price, stock, category_id):

        self.insert('', 0, text=name, values=(price, stock, category_id,))
    
    # Get selected item
    def get_selected_item(self):

        try:
             item_id = self.selection()[0]
             item_content = self.item(item_id)

             name = item_content['text']
             price = item_content['values'][0]
             stock = item_content['values'][1]
             category_id = item_content['values'][2]             
             return name, price, stock, category_id
        
        except IndexError as ie:
             print('Error: ',ie)
             return None
  
# CATEGORY MANAGER WINDOW
class CategoryManagerWindow(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Category Management')
        self.resizable(False, False)
        self.init_widgets()

    def init_widgets(self):
        
        # Add Frame
        add_frame = LabelFrame(self, text='Add Category')
        add_frame.grid(row=0, column=0, padx=10, pady=10, sticky='ew')

        Label(add_frame, text='Name:').grid(row=0, column=0, padx=5, pady=5)
        self.category_name_entry = Entry(add_frame)
        self.category_name_entry.grid(row=0, column=1, padx=5, pady=5)

        # Output message for the category window
        self.cat_message = Label(self, text='', fg='red')
        self.cat_message.grid(row=1, column=0, columnspan=2, sticky='ew')

        # Add Button, calling the Handler using the Entry
        self.btn_add = ttk.Button(add_frame, text='Add')
        self.btn_add.grid(row=0, column=2, padx=5, pady=5) 


        # TreeView for showing all categories (Just ID and Name)
        self.cat_tree = ttk.Treeview(self, columns=('#1'), height=8, selectmode='browse')
        
        self.cat_tree.heading('#0', text='ID', anchor=CENTER)
        self.cat_tree.heading('#1', text='Name', anchor=CENTER)

        self.cat_tree.column('#0', width=50, anchor=CENTER)
        self.cat_tree.column('#1', width=150, anchor=W)

        self.cat_tree.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky='ew')

        # Delete Category Button
        self.btn_delete = ttk.Button(self, text='Delete selected category')
        self.btn_delete.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky='ew')

    def get_name_input(self):
        return self.category_name_entry.get()
    
    def clear_input(self):
         
        self.category_name_entry.delete(0, END)

    def set_message(self, text, color='red'):
         
        self.cat_message['text'] = text
        self.cat_message['fg'] = color

    def load_tree_data(self, data_rows):

        for item in self.cat_tree.get_children():
            self.cat_tree.delete(item)

        for row in data_rows:
            self.cat_tree.insert('', 'end', text=row[0], values=(row[1],))


    def get_selected_category_name(self):

        try:
            
            item_id = self.cat_tree.selection()[0]
            return self.cat_tree.item(item_id)['values'][0]
        
        except IndexError:
            return None
        

# SUPPLIER MANAGER WINDOW
class SupplierManagerWindow(Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Supplier Management')
        self.resizable(False, False)
        self.init_widgets()

    def init_widgets(self):
        
        # Add Frame
        add_frame = LabelFrame(self, text='Add Supplier')
        add_frame.grid(row=0, column=0, padx=10, pady=10, sticky='ew')

        # Name
        Label(add_frame, text='Name:').grid(row=0, column=0, padx=5, pady=5)
        self.supplier_name_entry = Entry(add_frame)
        self.supplier_name_entry.grid(row=0, column=1, padx=5, pady=5)

        # Phone
        Label(add_frame, text='Phone:').grid(row=0, column=2, padx=5, pady=5)
        self.supplier_phone_entry = Entry(add_frame)
        self.supplier_phone_entry.grid(row=0, column=3, padx=5, pady=5)

        # Output message for the supplier window
        self.sup_message = Label(self, text='', fg='red')
        self.sup_message.grid(row=1, column=0, columnspan=2, sticky='ew')

        # Add Button, calling the Handler using the Entry
        self.btn_add = ttk.Button(add_frame, text='Add')
        self.btn_add.grid(row=0, column=4, padx=5, pady=5) 


        # TreeView for showing all suppliers 
        self.sup_tree = ttk.Treeview(self, columns=('#1', '#2'), height=8, selectmode='browse')
        
        self.sup_tree.heading('#0', text='ID', anchor=CENTER)
        self.sup_tree.heading('#1', text='Name', anchor=CENTER)
        self.sup_tree.heading('#2', text='Phone', anchor=CENTER)


        self.sup_tree.column('#0', width=50, anchor=CENTER)
        self.sup_tree.column('#1', width=150, anchor=W)
        self.sup_tree.column('#2', width=100, anchor=CENTER)

        self.sup_tree.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky='ew')

        # Delete Category Button
        self.btn_delete = ttk.Button(self, text='Delete selected supplier')
        self.btn_delete.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky='ew')

    def get_inputs(self):
        return self.supplier_name_entry.get(), self.supplier_phone_entry.get()
    
    def clear_inputs(self):
         
        self.supplier_name_entry.delete(0, END)
        self.supplier_phone_entry.delete(0, END)

    def set_message(self, text, color='red'):
         
        self.sup_message['text'] = text
        self.sup_message['fg'] = color

    def load_tree_data(self, data_rows):

        for item in self.sup_tree.get_children():
            self.sup_tree.delete(item)

        for row in data_rows:
            self.sup_tree.insert('', 'end', text=row[0], values=(row[1], row[2]))


    def get_selected_supplier_name(self):

        try:
            
            item_id = self.sup_tree.selection()[0]
            return self.sup_tree.item(item_id)['values'][0]
        
        except IndexError:
            return None
                      

# SALES PANEL USING SCALE, RADIOBUTTON AND OPTIONMENU
class SalesPanel(LabelFrame):

    def __init__(self, parent, logic_instance):
        super().__init__(parent, text = 'Point of Sale')
        self.logic = logic_instance
        self.init_widgets()
        self.load_products([])
        self.load_clients([])


    def init_widgets(self):

        # Product
        Label(self, text='Product:').grid(row=0, column=0)
        self.product_var = StringVar(self)
        self.product_opt = OptionMenu(self, self.product_var, "Select product...")
        self.product_opt.grid(row=0, column=1)

        # Quantity
        Label(self, text='Quantity:').grid(row=1, column=0)
        self.qty_spin = Spinbox(self, from_=1, to=100)
        self.qty_spin.grid(row=1, column=1)

        # Discount
        Label(self, text='Discount %:').grid(row=2, column=0)
        self.discount_scale = Scale(self, from_=0, to=50, orient=HORIZONTAL)
        self.discount_scale.grid(row=2, column=1)

        # Payment Method
        Label(self, text='Payment:').grid(row=3, column=0)
        self.pay_var = StringVar(value='Cash')
        Radiobutton(self, text='Cash', variable=self.pay_var, value='Cash').grid(row=3, column=1, sticky=W)
        Radiobutton(self, text='Card', variable=self.pay_var, value='Card').grid(row=4, column=1, sticky=W)

        # Client OptionMenu
        Label(self, text='Client Menu:').grid(row=5, column=0)        
        self.client_var = StringVar(self)
        self.client_opt = OptionMenu(self, self.client_var, "Select client...")
        self.client_opt.grid(row=5, column=1)

        # Sell Button
        self.btn_sell = Button(self, text='Confirm Sale')
        self.btn_sell.grid(row=7, columnspan=2, pady=10)

        # Message
        self.sale_message = Label(self, text='', fg='red')
        self.sale_message.grid(row=8, column=0, columnspan=2, pady=5)

    # Load products function
    def load_products(self, product_names):

        # Clear the current options and variable        
        menu = self.product_opt['menu']
        menu.delete(0, 'end')

        # Set the default variable text
        if product_names:

            self.product_var.set(product_names[0])

        else:
            self.product_var.set('No products available.')

        # Add new products
        for name in product_names:
            menu.add_command(label=name, command=lambda value=name: self.product_var.set(value))
    
    # Load clients function.
    def load_clients(self, client_names):

        # Clear the current options and variable        
        menu = self.client_opt['menu']
        menu.delete(0, 'end')

        # Set the default variable text
        if client_names:

            self.client_var.set(client_names[0])

        else:
            self.client_var.set('No clients available.')

        # Add new products
        for name in client_names:
            menu.add_command(label=name, command=lambda value=name: self.client_var.set(value))

    # Get all the sales data function
    def get_sale_data(self):

        return {
            'product_name': self.product_var.get(),
            'quantity': self.qty_spin.get(),
            'discount': self.discount_scale.get(),
            'payment_method': self.pay_var.get(),
            'client_name': self.client_var.get()
        }
    

    # Display the message in the sales panel function
    def set_message(self, text, color='blue'):
        
        self.sale_message['text'] = text
        self.sale_message['fg'] = color


    # Reset form function
    def reset_form(self):

        self.qty_spin.delete(0, END)
        self.qty_spin.insert(0, 1)
        self.discount_scale.set(0)
        self.pay_var.set('Cash')
        

# VISUAL DASHBOARD. Create a visual dashboard with a Canvas and a Listbox
class DashboardPanel(Frame):
    
    def __init__(self, parent):
        super().__init__(parent)

        # Canvas Widget
        Label(self, text='Sales Trends (Canvas)').pack(pady=5)
        self.canvas = Canvas(self, width=400, height=200, bg='white')
        self.canvas.pack(pady=5)

        # Draw bars
        self.draw_sales_graph([])

        # Listbox and Scrollbar widget (Logs History)
        Label(self, text='System Logs').pack()

        log_frame = Frame(self)
        log_frame.pack(padx=10)

        self.scrollbar = Scrollbar(log_frame)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.log_list = Listbox(log_frame, yscrollcommand=self.scrollbar.set, width=64, height=10)
        self.log_list.pack(side=LEFT)

        self.scrollbar.config(command=self.log_list.yview)

        # Message widget (Help)
        self.msg = Message(self, text='Welcome to the ERP System.', width=150)
        self.msg.pack(pady=10)

    def add_log(self, text):
        self.log_list.insert(END, text)
        self.log_list.see(END)

    def draw_sales_graph(self, sales_data):

        # Clear previous drawings
        self.canvas.delete('all')

        # Check if there is data
        if not sales_data:
            self.canvas.create_text(100, 50, text='No sales data available', fill='gray')
            return
        

        # Constants for drawing
        CANVAS_WIDTH = 400
        CANVAS_HEIGHT = 200
        BAR_WIDTH = 20
        PADDING = 20
        MAX_HEIGHT = CANVAS_HEIGHT - PADDING * 2

        # Get the maximum total sales to scale the bars
        max_total_sales = max(row[1] for row in sales_data)

        x_start = PADDING

        for name, total in sales_data:

            # Calculate proportional height
            bar_height = (total / max_total_sales) * MAX_HEIGHT

            # Bar coordinates
            x1 = x_start
            y1 = CANVAS_HEIGHT - PADDING
            x2 = x_start + BAR_WIDTH
            y2 = CANVAS_HEIGHT - PADDING - bar_height

            # Draw the bar (using different colors bases on position)
            color = 'blue' if x_start % 3 == 0 else ('green' if x_start % 3 == 1 else 'red')
            self.canvas.create_rectangle(x1, y1, x2, y2, fill=color)

            # Draw the category name below the bar
            self.canvas.create_text(x1 + BAR_WIDTH / 2, CANVAS_HEIGHT - 5, text=name, angle=0, anchor='c', font=('Arial', 7))

            # Move x_start for the next bar
            x_start += BAR_WIDTH + PADDING

            # Stop if we run out of canvas space
            if x_start > CANVAS_WIDTH - PADDING:
                break


# Client manager window class
class ClientManagerWindow(Toplevel):

    # Constructor
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Client Manager')
        self.transient(parent) # Keep the window above the main window
        self.grab_set()

        self.init_widgets()


    # Initialize widgets
    def init_widgets(self):

        # -- LEFT FRAME: Form to add/delete clients --

        left_frame = Frame(self, padx=10, pady=10)
        left_frame.grid(row=0, column=0, sticky='ns')

        Label(left_frame, text='Cliente Registration', font=('Arial', 10, 'bold')).pack(pady=5)

        # Name Input
        Label(left_frame, text='Name:').pack(pady=2)
        self.name_input = Entry(left_frame)
        self.name_input.pack(fill=X, padx=5)

        # Email Input
        Label(left_frame, text='Email:').pack(pady=2)
        self.email_imput = Entry(left_frame)
        self.email_imput.pack(fill=X, padx=5)

        # Notes Textbox
        Label(left_frame, text='Notes:').pack(pady=2)
        self.notes_text = Text(left_frame, height=5, width=30)
        self.notes_text.pack(fill=X, padx=5)

        # Message Label (for feedback)
        self.message = Label(left_frame, text='', fg='red')
        self.message.pack(pady=5)

        # Button Frame
        button_frame = Frame(left_frame)
        button_frame.pack(pady=10)

        # Add Button (command will be set in main.py)
        self.add_button = Button(button_frame, text='Add Client', bg='green', fg='white')
        self.add_button.pack(side=LEFT, padx=5)

        # Delete Button (command will be set in main.py)
        self.delete_button = Button(button_frame, text='Delete Selected', bg='red', fg='white')
        self.delete_button.pack(side=LEFT, padx=5)

        
        # -- RIGHT FRAME: TreeView for displaying Clients -- 
        right_frame = Frame(self, padx=10, pady=10)
        right_frame.grid(row=0, column=1, sticky='nsew')
        self.grid_columnconfigure(1, weight=1) # Make the TreeView Frame expandable

        # TreeView setup
        self.tree = ttk.Treeview(right_frame, columns=('Name','Email','Notes',), show='headings')
        self.tree.heading('Name', text='Name')
        self.tree.heading('Email', text='Email')
        self.tree.heading('Notes', text='Notes')

        # Set widths of the columns
        self.tree.column('Name', width=150)
        self.tree.column('Email', width=150)
        self.tree.column('Notes', width=250)

        self.tree.pack(side=LEFT, fill=BOTH, expand=True)

        # Scrollbar
        scrollbar = Scrollbar(right_frame, orient='vertical', command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=RIGHT, fill=Y)


    # Method to retrieve form data
    def get_inputs(self):
        name = self.name_input.get()
        email = self.email_imput.get()
        notes = self.notes_text.get('1.0', END).strip()
        
        return name, email, notes
    
    # Method to clear form inputs
    def clear_inputs(self):
        self.name_input.delete(0, END)
        self.email_imput.delete(0, END)
        self.notes_text.delete('1.0', END)

    # Method to set message feedback
    def set_message(self, text, color='black'):
        self.message.config(text=text, fg=color)

    # Method to load data into the Treeview
    def load_tree_data(self, data_rows):
        
        # Clear the inpus
        for row in self.tree.get_children():
            self.tree.delete(row)

        # Insert new data
        for row in data_rows:

            self.tree.insert('', END, values=(row[1], row[2], row[3]))

    # Method to get the selected cliente name for deletion
    def get_selected_client_name(self):
        selected_item = self.tree.focus()

        if selected_item:

            # Asume the name is the first values in the row
            return self.tree.item(selected_item)['values'][0]
        
        return None
    

# Sales Report Window
class SalesReportWindow(Toplevel):

    def __init__(self, parent):
        super().__init__(parent)
        self.title('Sales Report History')
        self.geometry('1200x600')
        self.transient(parent) # It makes the window visualize above the main window
        self.init_widgets()

    
    def init_widgets(self):

        # Title
        Label(self, text='Sales History', font=('Arial', 14, 'bold')).pack(pady=10)

        # Treeview Frame
        tree_frame = Frame(self)
        tree_frame.pack(fill=BOTH, expand=True, padx=10, pady=10)

        # Scrollbar
        scrollbar = Scrollbar(tree_frame)
        scrollbar.pack(side=RIGHT, fill=Y)

        # Treeview Configuration
        columns = ('id','product','client','quantity','total','date')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', yscrollcommand=scrollbar.set)

        # Headers
        self.tree.heading('id', text='ID')
        self.tree.heading('product', text='Product')
        self.tree.heading('client', text='Client')
        self.tree.heading('quantity', text='Quantity')
        self.tree.heading('total', text='Total ($)')
        self.tree.heading('date', text='Date')

        # Columns dimensions
        self.tree.column('id', width=40, anchor=CENTER)
        self.tree.column('product', width=150)
        self.tree.column('client', width=150)
        self.tree.column('quantity', width=50, anchor=CENTER)
        self.tree.column('total', width=100, anchor=E)
        self.tree.column('date', width=150, anchor=CENTER)

        self.tree.pack(side=LEFT, fill=BOTH, expand=True)
        scrollbar.config(command=self.tree.yview)

        # Close Button
        Button(self, text='Close', command=self.destroy, bg='gray', fg='white').pack(pady=10)


    # Load data function
    def load_data(self, data_rows):

        for row in self.tree.get_children():
            self.tree.delete(row)


        for row in data_rows:

            id_sale, prod, cli, qty, total, date = row
            total_formatted = f"{total:.2f}"

            self.tree.insert('', END, values=(id_sale, prod, cli, qty, total_formatted, date))      






