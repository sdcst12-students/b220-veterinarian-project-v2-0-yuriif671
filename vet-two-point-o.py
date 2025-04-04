import sqlite3

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


def addCustomer():
    conn = sqlite3.connect("veterinarian.db")
    cursor = conn.cursor()
    
    fname = input("Enter first name: ")
    lname = input("Enter last name: ")
    phone = input("Enter phone number: ")
    email = input("Enter email: ")
    address = input("Enter address: ")
    city = input("Enter city: ")
    postalcode = input("Enter postal code: ")
    
    cursor.execute("SELECT id FROM customers WHERE phone = ? OR email = ?", (phone, email))
    existing_customer = cursor.fetchone()
    
    if existing_customer:
        print("There is already a username with the same phone number or email")
        conn.close()
        return
    
    cursor.execute("SELECT id, fname, lname FROM customers WHERE lname = ?", (lname,))
    matching_customers = cursor.fetchall()
    
    if matching_customers:
        print("Customers with the same last name found:")
        for customer in matching_customers:
            print(f"ID: {customer[0]}, Name: {customer[1]} {customer[2]}")
        confirm = input("Do you still want to add? (Y/n): ")
        if confirm != "Y":
            print("Customer not added.")
            conn.close()
            return
    
    cursor.execute('''
        INSERT INTO customers (fname, lname, phone, email, address, city, postalcode)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (fname, lname, phone, email, address, city, postalcode))
    
    conn.commit()
    conn.close()
    print("Customer added successfully.")


def searchCustomer():
    conn = sqlite3.connect("veterinarian.db")
    cursor = conn.cursor()
    
    search_term = input("\nEnter any field value to find customer: ")
    
    cursor.execute('''
        SELECT * FROM customers
        WHERE fname = ? OR lname = ? OR phone = ? OR email = ? OR city = ? OR address = ? OR postalcode = ?
    ''', (search_term,) * 7)
    
    results = cursor.fetchone()
    
    if results:
        print(f"""
    ID         : {results[0]}
    First Name : {results[1]}
    Last Name  : {results[2]}
    Phone Num  : {results[3]}
    Email      : {results[4]}
    Address    : {results[5]}
    City       : {results[6]}
    Postal Code: {results[7]}
        """)
    else:
        print("No matches found")
    conn.close()


def updateData(id, data):
    conn = sqlite3.connect("veterinarian.db")
    cursor = conn.cursor()

    values = list(data.values())
    values.append(id)  
    
    cursor.execute(f'''
        UPDATE customers 
        SET {', '.join([f"{key} = ?" for key in data.keys()])} 
        WHERE id = ?
    ''', values)
    
    conn.commit()
    conn.close()
    print("Customer data updated successfully.")


def editCustomer():
    conn = sqlite3.connect("veterinarian.db")
    cursor = conn.cursor()

    id_input = input("Enter the ID of the customer you want to edit: ")
    
    cursor.execute('''
        SELECT id, fname, lname, phone, email, address, city, postalcode 
        FROM customers 
        WHERE id = ?
    ''', (id_input,))
    
    customer = cursor.fetchone()
    
    if customer:
        print(f"""
    ID         : {customer[0]}
    First Name : {customer[1]}
    Last Name  : {customer[2]}
    Phone Num  : {customer[3]}
    Email      : {customer[4]}
    Address    : {customer[5]}
    City       : {customer[6]}
    Postal Code: {customer[7]}
        """)


        while True:
            print("""
    A: change first name
    B: change last name
    C: change phone number
    D: change email
    E: change address
    F: change city
    G: change postal code
    I: finish update
            """)


            choice = input(">>> ").upper()

            if choice == 'A':
                new_value = input("Enter new First Name: ")
                data = {"fname": new_value}
            elif choice == 'B':
                new_value = input("Enter new Last Name: ")
                data = {"lname": new_value}
            elif choice == 'C':
                new_value = input("Enter new Phone Number: ")
                data = {"phone": new_value}
            elif choice == 'D':
                new_value = input("Enter new Email: ")
                data = {"email": new_value}
            elif choice == 'E':
                new_value = input("Enter new Address: ")
                data = {"address": new_value}
            elif choice == 'F':
                new_value = input("Enter new City: ")
                data = {"city": new_value}
            elif choice == 'G':
                new_value = input("Enter new Postal Code: ")
                data = {"postalcode": new_value}
            elif choice == 'I':
                updateData(id_input, data)
                break
            else:
                print("Invalid choice. Please choose again.")
    else:
        print("Customer not found.")
    
    conn.close()

def main():
    action = input("What do you want to do? Add customer, search customer, or edit customer? (add/search/edit): ")
    
    if action == "add":
        addCustomer()
    elif action == "search":
        searchCustomer()
    elif action == "edit":
        editCustomer()
    else:
        print("Invalid choice. Please choose 'add', 'search', or 'edit'.")

if __name__ == "__main__":
    main()