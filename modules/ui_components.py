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

        # Sell Button
        self.btn_sell = Button(self, text='Confirm Sale')
        self.btn_sell.grid(row=5, columnspan=2, pady=10)

        # Message
        self.sale_message = Label(self, text='', fg='red')
        self.sale_message.grid(row=6, column=0, columnspan=2, pady=5)

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
    
    # Get all the sales data function
    def get_sale_data(self):

        return {
            'product_name': self.product_var.get(),
            'quantity': self.qty_spin.get(),
            'discount': self.discount_scale.get(),
            'payment_method': self.pay_var.get()
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
        self.canvas = Canvas(self, width=200, height=100, bg='white')
        self.canvas.pack(pady=5)

        # Draw single bars
        self.canvas.create_rectangle(10, 80, 30, 20, fill='blue')
        self.canvas.create_rectangle(40, 80, 60, 50, fill='green')
        self.canvas.create_rectangle(70, 80, 90, 10, fill='red')

        # Listbox and Scrollbar widget (Logs History)
        Label(self, text='System Logs').pack()

        log_frame = Frame(self)
        log_frame.pack(fill=X, padx=10)

        self.scrollbar = Scrollbar(log_frame)
        self.scrollbar.pack(side=RIGHT, fill=Y)

        self.log_list = Listbox(log_frame, yscrollcommand=self.scrollbar.set, height=5)
        self.log_list.pack(side=LEFT)

        self.scrollbar.config(command=self.log_list.yview)

        # Message widget (Help)
        self.msg = Message(self, text='Welcome to the ERP System.', width=150)
        self.msg.pack(pady=10)

    def add_log(self, text):
        self.log_list.insert(END, text)
        self.log_list.see(END)