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

            # Save Button. 
            # We dont add the command arguments yet, because will main.py do
            self.save_button = ttk.Button(self,text='Save Product')
            self.save_button.grid(row=5,columnspan=3, sticky=W+E, pady=2,padx=5)    

            # Output message
            self.message = Label(text='', fg='red')
            self.message.grid(row=6, column=0, columnspan=3, sticky=W + E)

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
        self.btn_add = ttk.Button(add_frame, text='Add', command='')
        self.btn_add.grid(row=0, column=2, padx=5, pady=5) 


        # TreeView for showing all categories (Just ID and Name)
        self.cat_tree = ttk.Treeview(self, columns=('#1'), height=8, selectmode='browse')
        
        self.cat_tree.heading('#0', text='ID', anchor=CENTER)
        self.cat_tree.heading('#1', text='Name', anchor=CENTER)

        self.cat_tree.column('#0', width=50, anchor=CENTER)
        self.cat_tree.column('#1', width=150, anchor=W)

        self.cat_tree.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky='ew')

        # Delete Category Button
        self.btn_delete = ttk.Button(self, text='Delete selected category', command='')
        self.btn_delete.grid(row=3, column=0, columnspan=2, padx=10, pady=5, sticky='ew')

    def get_name_input(self):
        return self.category_name_entry.get()
    
    def clear_input(self):
         
        self.category_name_entry.delete(0, END)

    def set_message(self, text, color='red'):
         
        self.message_label['text'] = text
        self.message_label['fg'] = color

    def load_tree_data(self, data_rows):

        for item in self.tree.get_children():
            self.tree.delete(item)

        for row in data_rows:
            self.tree.insert('', 'end', text=row[0], values=(row[1],))


    def get_selected_category_name(self):

        try:
            
            item_id = self.tree.selection()[0]
            return self.tree.item(item_id)['values'][0]
        
        except IndexError:
            return None
                      