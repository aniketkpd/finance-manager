import sqlite3

# Creating all necessary tables at first
def init_db():

    # Creating and connecting database
    conn = sqlite3.connect("finance.db")
    c = conn.cursor()

    # Creating users table
    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS users(
            uid INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
        '''
    )

    # Creating profiles table
    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS profiles(
        pid INTEGER PRIMARY KEY AUTOINCREMENT,
        uid INTEGER,
        name TEXT,
        phone TEXT,
        about TEXT,
        dob DATE,
        profile_photo TEXT,
        FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE
        );
        '''
    )




    # Creating categories table with user-specific categories
    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS categories (
            cid INTEGER PRIMARY KEY AUTOINCREMENT,
            uid INTEGER,  -- Allows user-specific categories
            name TEXT NOT NULL,
            description TEXT,
            type TEXT CHECK(type IN ('Income', 'Expense')) NOT NULL,
            UNIQUE(name, uid),  -- Ensures a user cannot create duplicate categories, but different users can have the same category name
            FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE
        );
        '''
    )





    # Creating transactions table
    c.execute(
    '''
    CREATE TABLE IF NOT EXISTS transactions (
        tid INTEGER PRIMARY KEY AUTOINCREMENT,
        uid INTEGER,
        cid INTEGER,
        date DATE NOT NULL,
        type TEXT CHECK(type IN ('Income', 'Expense')) NOT NULL,
        amount INTEGER NOT NULL,
        description TEXT,
        payment_method TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE,
        FOREIGN KEY (cid) REFERENCES categories(cid) ON DELETE CASCADE
    );
    '''
)


    # Creating budget table
    c.execute(
        '''
        CREATE TABLE IF NOT EXISTS budget (
        bid INTEGER PRIMARY KEY AUTOINCREMENT,
        uid INTEGER,
        cid INTEGER,
        amount INTEGER NOT NULL,
        start_date DATE, 
        end_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (uid) REFERENCES users(uid) ON DELETE CASCADE,
        FOREIGN KEY (cid) REFERENCES categories(cid) ON DELETE CASCADE
        );
        '''
    )

    # Saving all changes
    conn.commit()
    conn.close()

    print("Database created successfully.")




def defualt_categories_inserter():

    conn = sqlite3.connect("finance.db")
    c = conn.cursor()

    base_categories = [
        ("Food", "Expenses on food and groceries", "Expense"),
        ("Entertainment", "Leisure and entertainment costs", "Expense"),
        ("Transport", "Travel and commuting expenses", "Expense"),
        ("Salary", "Income from salary or wages", "Income"),
        ("Freelancing", "Earnings from freelance work", "Income"),
        ("Investments", "Income from investments", "Income")
    ]

    for name, description, type_ in base_categories:
        c.execute(
            '''
            INSERT OR IGNORE INTO categories (uid, name, description, type) 
            VALUES (0, ?, ?, ?)
            ''', 
            (name, description, type_)
        )

    conn.commit()
    conn.close()
    print("Defualt categories added successfully!")
    
    
init_db()
defualt_categories_inserter()