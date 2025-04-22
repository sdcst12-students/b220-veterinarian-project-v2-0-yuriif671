import tkinter as tk
from tkinter import messagebox
import sqlite3
import re

def init_db():
    conn = sqlite3.connect("veterinarian.db")
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS customers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fname TEXT,
            lname TEXT,
            phone TEXT,
            email TEXT UNIQUE,
            address TEXT,
            city TEXT,
            postalcode TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            type TEXT,
            breed TEXT,
            birthdate DATE,
            ownerID INTEGER,
            FOREIGN KEY (ownerID) REFERENCES customers(id) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS visits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ownerid INTEGER,
            petid INTEGER,
            details TEXT,
            cost REAL,
            paid REAL,
            FOREIGN KEY (ownerid) REFERENCES customers(id) ON DELETE CASCADE,
            FOREIGN KEY (petid) REFERENCES pets(id) ON DELETE CASCADE
        )
    ''')

    conn.commit()
    conn.close()


def add_customer_window():
    def submit():
        fname = entry_fname.get()
        lname = entry_lname.get()
        phone = entry_phone.get()
        email = entry_email.get()
        address = entry_address.get()
        city = entry_city.get()
        postalcode = entry_postalcode.get()

        conn = sqlite3.connect("veterinarian.db")
        cursor = conn.cursor()

        if '' in [fname, lname, phone, email, address, city, postalcode]:
            messagebox.showerror("Empty", "Missing some values")
            conn.close()
            return
        
       
        if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) == None:
            messagebox.showerror("Bad Email", "You are stupid")
            conn.close()
            return
        
        if re.match(r'^\d{10,15}$', phone) == None:
            messagebox.showerror("Bad Phone", "You are stupid")
            conn.close()
            return
        
        cursor.execute("SELECT id FROM customers WHERE phone = ? OR email = ?", (phone, email))
        if cursor.fetchone():
            messagebox.showerror("Duplicate", "Phone number or email already exists.")
            conn.close()
            return

        cursor.execute('''
            INSERT INTO customers (fname, lname, phone, email, address, city, postalcode)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (fname, lname, phone, email, address, city, postalcode))

        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Customer added successfully.")
        add_win.destroy()

    add_win = tk.Toplevel(root)
    add_win.title("Add Customer")

    fields = ["First Name", "Last Name", "Phone", "Email", "Address", "City", "Postal Code"]
    entries = []
    for idx, field in enumerate(fields):
        tk.Label(add_win, text=field).grid(row=idx, column=0, sticky="e")
    
    entry_fname = tk.Entry(add_win); entry_fname.grid(row=0, column=1)
    entry_lname = tk.Entry(add_win); entry_lname.grid(row=1, column=1)
    entry_phone = tk.Entry(add_win); entry_phone.grid(row=2, column=1)
    entry_email = tk.Entry(add_win); entry_email.grid(row=3, column=1)
    entry_address = tk.Entry(add_win); entry_address.grid(row=4, column=1)
    entry_city = tk.Entry(add_win); entry_city.grid(row=5, column=1)
    entry_postalcode = tk.Entry(add_win); entry_postalcode.grid(row=6, column=1)

    tk.Button(add_win, text="Submit", command=submit).grid(row=7, column=0, columnspan=2)


def search_customer_window():
    def search():
        search_term = entry_search.get()
        conn = sqlite3.connect("veterinarian.db")
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM customers
            WHERE fname = ? OR lname = ? OR phone = ? OR email = ? OR city = ? OR address = ? OR postalcode = ?
        ''', (search_term,) * 7)
        result = cursor.fetchone()
        conn.close()

        if result:
            output = f"""
ID: {result[0]}
Name: {result[1]} {result[2]}
Phone: {result[3]}
Email: {result[4]}
Address: {result[5]}, {result[6]}, {result[7]}
"""
            messagebox.showinfo("Customer Found", output)
        else:
            messagebox.showwarning("Not Found", "No matching customer found.")

    search_win = tk.Toplevel(root)
    search_win.title("Search Customer")

    tk.Label(search_win, text="Enter any field value:").pack()
    entry_search = tk.Entry(search_win)
    entry_search.pack()
    tk.Button(search_win, text="Search", command=search).pack()

def edit_customer_window():
    def load_customer():
        cust_id = entry_id.get()
        conn = sqlite3.connect("veterinarian.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE id = ?", (cust_id,))
        customer = cursor.fetchone()
        conn.close()

        if customer:
            for i, entry in enumerate(edit_entries):
                entry.delete(0, tk.END)
                entry.insert(0, customer[i + 1])
            btn_save.config(state=tk.NORMAL)
        else:
            messagebox.showerror("Error", "Customer not found.")

    def save_changes():
        cust_id = entry_id.get()
        updated = [entry.get() for entry in edit_entries]

        conn = sqlite3.connect("veterinarian.db")
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE customers 
            SET fname = ?, lname = ?, phone = ?, email = ?, address = ?, city = ?, postalcode = ?
            WHERE id = ?
        ''', (*updated, cust_id))
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Customer updated.")
        edit_win.destroy()

    edit_win = tk.Toplevel(root)
    edit_win.title("Edit Customer")

    tk.Label(edit_win, text="Enter Customer ID:").grid(row=0, column=0)
    entry_id = tk.Entry(edit_win)
    entry_id.grid(row=0, column=1)
    tk.Button(edit_win, text="Load", command=load_customer).grid(row=0, column=2)

    labels = ["First Name", "Last Name", "Phone", "Email", "Address", "City", "Postal Code"]
    edit_entries = []
    for i, label in enumerate(labels):
        tk.Label(edit_win, text=label).grid(row=i+1, column=0)
        entry = tk.Entry(edit_win)
        entry.grid(row=i+1, column=1)
        edit_entries.append(entry)

    btn_save = tk.Button(edit_win, text="Save Changes", command=save_changes, state=tk.DISABLED)
    btn_save.grid(row=8, column=0, columnspan=2)


init_db()
root = tk.Tk()
root.title("Veterinarian Customer Management")

tk.Label(root, text="Veterinarian Customer Management System", font=("Arial", 16)).pack(pady=10)

tk.Button(root, text="Add Customer", width=20, command=add_customer_window).pack(pady=5)
tk.Button(root, text="Search Customer", width=20, command=search_customer_window).pack(pady=5)
tk.Button(root, text="Edit Customer", width=20, command=edit_customer_window).pack(pady=5)

root.mainloop()