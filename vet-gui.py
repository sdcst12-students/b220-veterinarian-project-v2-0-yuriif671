import tkinter as tk
from tkinter import messagebox
import sqlite3
import re

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

# validate data
def isEmail(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def isPhone(phone):
    return phone.isdigit() and len(phone) == 10

def isPostal(code):
    return re.match(r"^[A-Za-z]\d[A-Za-z][ -]?\d[A-Za-z]\d$", code)

###
def validateAll(fields):
    fname, lname, phone, email, address, city, postalcode = fields
    if not all(fields):
        return "All fields must be filled."
    if not isPhone(phone):
        return "Phone number must be exactly 10 digits."
    if not isEmail(email):
        return "Invalid email format."
    if not isPostal(postalcode):
        return "Invalid Canadian postal code format (e.g., V8W 1N6)."
    return None


root = tk.Tk()
root.title("Veterinary Database GUI")
root.configure(bg="black")
root.attributes('-fullscreen', True)

### nav and screens
def clear():
    for widget in root.winfo_children():
        widget.destroy()

def goBack():
    clear()
    main()

def main():
    clear()
    frame = tk.Frame(root, bg="black")
    frame.pack(expand=True)

    title = tk.Label(frame, text="Veterinary Database", font=("Helvetica", 32), fg="white", bg="black")
    title.pack(pady=20)

    buttons = [
        ("Add Customer", addCustomer),
        ("Search Customer", searchCustomer),
        ("Edit Customer", editCustomer),
        ("Exit", root.quit)
    ]

    for text, command in buttons:
        b = tk.Button(frame, text=text, font=("Helvetica", 16), width=20, command=command,
                      bg="gray12", fg="white", activebackground="#2C2C2C")
        b.pack(pady=10)


## db operations
def addCustomer():
    clear()
    frame = tk.Frame(root, bg="black")
    frame.pack(expand=True)

    fields = ["First Name", "Last Name", "Phone", "Email", "Address", "City", "Postal Code"]
    entries = []

    for field in fields:
        tk.Label(frame, text=field, fg="white", bg="black", font=("Helvetica", 14)).pack()
        entry = tk.Entry(frame, font=("Helvetica", 14), bg="gray12", fg="white", insertbackground="white")
        entry.pack(pady=5)
        entries.append(entry)

    def submit():
        values = [e.get().strip() for e in entries]
        error = validateAll(values)
        if error:
            messagebox.showerror("Validation Error", error)
            return

        conn = sqlite3.connect("veterinarian.db")
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM customers WHERE phone = ? OR email = ?", (values[2], values[3]))
        if cursor.fetchone():
            messagebox.showwarning("Duplicate", "A customer with this phone or email already exists.")
            conn.close()
            return

        # all good insert
        cursor.execute('''
            INSERT INTO customers (fname, lname, phone, email, address, city, postalcode)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', values)
        conn.commit()
        conn.close()
        messagebox.showinfo("Success", "Customer added successfully.")
        goBack()

    # controls
    tk.Button(frame, text="Submit", command=submit, font=("Helvetica", 14),
              bg="gray12", fg="white", activebackground="#2C2C2C").pack(pady=10)
    tk.Button(frame, text="Go Back", command=goBack, font=("Helvetica", 12),
              bg="#333333", fg="white").pack()

def searchCustomer():
    clear()
    frame = tk.Frame(root, bg="black")
    frame.pack(expand=True)

    tk.Label(frame, text="Search for customer by any field", font=("Helvetica", 16), fg="white", bg="black").pack(pady=10)
    entry = tk.Entry(frame, font=("Helvetica", 14), bg="gray12", fg="white", insertbackground="white")
    entry.pack(pady=10)

    output = tk.Text(frame, height=10, width=70, bg="gray12", fg="white", font=("Helvetica", 12))
    output.pack(pady=10)

    def search():
        term = entry.get().strip()
        if not term:
            messagebox.showerror("Error", "Please enter a search term.")
            return

        conn = sqlite3.connect("veterinarian.db")
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM customers
            WHERE fname = ? OR lname = ? OR phone = ? OR email = ? OR city = ? OR address = ? OR postalcode = ?
        ''', (term,) * 7)
        matches = cursor.fetchall()
        conn.close()


        #this deletes all previous text in the output field
        output.delete(1.0, tk.END)
        if matches:
            for m in matches:
                output.insert(tk.END, f"ID: {m[0]}\nName: {m[1]} {m[2]}\nPhone: {m[3]}\nEmail: {m[4]}\n"
                                           f"Address: {m[5]}, {m[6]}, {m[7]}\n\n")
        else:
            output.insert(tk.END, "No matches found.")

    tk.Button(frame, text="Search", command=search, font=("Helvetica", 14),
              bg="gray12", fg="white", activebackground="#2C2C2C").pack(pady=5)
    tk.Button(frame, text="Go Back", command=goBack, font=("Helvetica", 12),
              bg="#333333", fg="white").pack()

def editCustomer():
    clear()
    frame = tk.Frame(root, bg="black")
    frame.pack(expand=True)

    tk.Label(frame, text="Enter customer ID to edit", font=("Helvetica", 16), fg="white", bg="black").pack(pady=10)
    id = tk.Entry(frame, font=("Helvetica", 14), bg="gray12", fg="white", insertbackground="white")
    id.pack(pady=10)

    def load():
        cid = id.get().strip()
        if not cid.isdigit():
            messagebox.showerror("Error", "Customer ID must be a number.")
            return

        conn = sqlite3.connect("veterinarian.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM customers WHERE id = ?", (cid,))
        customer = cursor.fetchone()
        conn.close()

        if not customer:
            messagebox.showerror("Error", "Customer not found.")
            return

        clear()

        edit_frame = tk.Frame(root, bg="black")
        edit_frame.pack(expand=True)

        fields = ["First Name", "Last Name", "Phone", "Email", "Address", "City", "Postal Code"]
        entries = []

        for i, field in enumerate(fields, start=1):
            tk.Label(edit_frame, text=field, fg="white", bg="black", font=("Helvetica", 14)).pack()
            entry = tk.Entry(edit_frame, font=("Helvetica", 14), bg="gray12", fg="white", insertbackground="white")
            entry.insert(0, customer[i])
            entry.pack(pady=5)
            entries.append(entry)

        def submitEdit():
            values = [e.get().strip() for e in entries]
            error = validateAll(values)
            if error:
                messagebox.showerror("Validation Error", error)
                return

            conn = sqlite3.connect("veterinarian.db")
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE customers SET fname=?, lname=?, phone=?, email=?, address=?, city=?, postalcode=? WHERE id=?
            ''', (*values, cid))
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "Customer updated.")
            goBack()

        tk.Button(edit_frame, text="Update", command=submitEdit, font=("Helvetica", 14),
                  bg="gray12", fg="white", activebackground="#2C2C2C").pack(pady=10)
        tk.Button(edit_frame, text="Go Back", command=goBack, font=("Helvetica", 12),
                  bg="#333333", fg="white").pack()

    tk.Button(frame, text="Load Customer", command=load, font=("Helvetica", 14),
              bg="gray12", fg="white", activebackground="#2C2C2C").pack(pady=10)
    tk.Button(frame, text="Go Back", command=goBack, font=("Helvetica", 12),
              bg="#333333", fg="white").pack()

main()
root.mainloop()