import sqlite3


class Database:
    def __init__(self, db_name):
        self.db_name = db_name

    def connect(self):
        return sqlite3.connect(self.db_name)

    def create_tables(self):
        conn = self.connect()
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


class Customer:
    def __init__(self, db, id=None, fname=None, lname=None, phone=None, email=None, address=None, city=None, postalcode=None):
        self.db = db
        self.id = id
        self.fname = fname
        self.lname = lname
        self.phone = phone
        self.email = email
        self.address = address
        self.city = city
        self.postalcode = postalcode

    def add(self):
        conn = self.db.connect()
        cursor = conn.cursor()

        cursor.execute("SELECT id FROM customers WHERE phone = ? OR email = ?", (self.phone, self.email))
        existing_customer = cursor.fetchone()

        if existing_customer:
            print("There is already a customer with the same phone number or email.")
            conn.close()
            return

        cursor.execute("SELECT id, fname, lname FROM customers WHERE lname = ?", (self.lname,))
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
        ''', (self.fname, self.lname, self.phone, self.email, self.address, self.city, self.postalcode))

        conn.commit()
        conn.close()
        print("Customer added successfully.")

    @staticmethod
    def search(db, search_term):
        conn = db.connect()
        cursor = conn.cursor()

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

    def update(self):
        conn = self.db.connect()
        cursor = conn.cursor()

        cursor.execute(f'''
            UPDATE customers 
            SET fname = ?, lname = ?, phone = ?, email = ?, address = ?, city = ?, postalcode = ? 
            WHERE id = ?
        ''', (self.fname, self.lname, self.phone, self.email, self.address, self.city, self.postalcode, self.id))

        conn.commit()
        conn.close()
        print("Customer data updated successfully.")


class CustomerEditor:
    def __init__(self, db):
        self.db = db

    def edit_customer(self):
        id_input = input("Enter the ID of the customer you want to edit: ")
        conn = self.db.connect()
        cursor = conn.cursor()

        cursor.execute('''
            SELECT id, fname, lname, phone, email, address, city, postalcode 
            FROM customers 
            WHERE id = ?
        ''', (id_input,))

        customer_data = cursor.fetchone()

        if customer_data:
            customer = Customer(self.db, *customer_data)
            print(f"""
    ID         : {customer.id}
    First Name : {customer.fname}
    Last Name  : {customer.lname}
    Phone Num  : {customer.phone}
    Email      : {customer.email}
    Address    : {customer.address}
    City       : {customer.city}
    Postal Code: {customer.postalcode}
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
                    customer.fname = input("Enter new First Name: ")
                elif choice == 'B':
                    customer.lname = input("Enter new Last Name: ")
                elif choice == 'C':
                    customer.phone = input("Enter new Phone Number: ")
                elif choice == 'D':
                    customer.email = input("Enter new Email: ")
                elif choice == 'E':
                    customer.address = input("Enter new Address: ")
                elif choice == 'F':
                    customer.city = input("Enter new City: ")
                elif choice == 'G':
                    customer.postalcode = input("Enter new Postal Code: ")
                elif choice == 'I':
                    customer.update()
                    break
                else:
                    print("Invalid choice. Please choose again.")
        else:
            print("Customer not found.")
        
        conn.close()


def main():
    db = Database("veterinarian.db")
    db.create_tables()

    action = input("What do you want to do? Add customer, search customer, or edit customer? (add/search/edit): ")

    if action == "add":
        fname = input("Enter first name: ")
        lname = input("Enter last name: ")
        phone = input("Enter phone number: ")
        email = input("Enter email: ")
        address = input("Enter address: ")
        city = input("Enter city: ")
        postalcode = input("Enter postal code: ")
        customer = Customer(db, fname=fname, lname=lname, phone=phone, email=email, address=address, city=city, postalcode=postalcode)
        customer.add()

    elif action == "search":
        search_term = input("Enter search term: ")
        Customer.search(db, search_term)

    elif action == "edit":
        editor = CustomerEditor(db)
        editor.edit_customer()

    else:
        print("Invalid choice. Please choose 'add', 'search', or 'edit'")


if __name__ == "__main__":
    main()