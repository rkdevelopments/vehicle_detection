#adding new column in exiting db
"""import sqlite3

# Database and table details
DB_NAME = 'cam1.db'
TABLE_NAME = 'vehicle_data'
NEW_COLUMN_NAME = 'number_plate'
NEW_COLUMN_TYPE = 'TEXT'

def add_column_if_not_exists():
    # Connect to the database
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Check existing columns
    cursor.execute(f"PRAGMA table_info({TABLE_NAME});")
    columns = [col[1] for col in cursor.fetchall()]

    # Add column if not exists
    if NEW_COLUMN_NAME not in columns:
        alter_query = f"ALTER TABLE {TABLE_NAME} ADD COLUMN {NEW_COLUMN_NAME} {NEW_COLUMN_TYPE};"
        cursor.execute(alter_query)
        conn.commit()
        print(f"Column '{NEW_COLUMN_NAME}' added to '{TABLE_NAME}' table.")
    else:
        print(f"Column '{NEW_COLUMN_NAME}' already exists in '{TABLE_NAME}' table.")

    # Close the connection
    conn.close()

if __name__ == "__main__":
    add_column_if_not_exists()"""

# retriving db
"""import sqlite3

# Database name
DB_NAME = 'cam1.db'

def get_table_structure(table_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Get table structure
    cursor.execute(f"PRAGMA table_info({table_name});")
    columns = cursor.fetchall()

    if columns:
        print(f"\nTable: {table_name}")
        print("-" * 40)
        print("{:<5} {:<20} {:<10}".format("ID", "Column Name", "Type"))
        print("-" * 40)
        for col in columns:
            print("{:<5} {:<20} {:<10}".format(col[0], col[1], col[2]))
    else:
        print(f"No table named '{table_name}' found.")

    conn.close()

def list_all_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # Get all tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    if tables:
        print("Tables in Database:")
        print("-" * 40)
        for table in tables:
            print(table[0])
            get_table_structure(table[0])
    else:
        print("No tables found in the database.")

    conn.close()

if __name__ == "__main__":
    list_all_tables()"""

# creating database"""
"""import sqlite3

def create_database_structure():
    try:
        # Connect to the database (this will create the database if it doesn't exist)
        conn = sqlite3.connect('camera.db')  # Changed the database name here
        cursor = conn.cursor()
        
        # Create table for Camera 1
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicle_data1 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_count INTEGER,
            exit_count INTEGER,
            entry_time TEXT,
            exit_time TEXT,
            vehicle_snapshot BLOB
        )
        ''')
        print("Table vehicle_data_cam1 created or already exists.")
        
        # Create table for Camera 2
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS vehicle_data2 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_count INTEGER,
            exit_count INTEGER,
            entry_time TEXT,
            exit_time TEXT,
            vehicle_snapshot BLOB
        )
        ''')
        print("Table vehicle_data_cam2 created or already exists.")
        
        # Commit changes and close the connection
        conn.commit()
        conn.close()
        print("Database structure created successfully in camera.db.")
    
    except sqlite3.Error as e:
        print(f"Error creating database structure: {e}")

# Run the script to create the database structure
create_database_structure()"""

# delete entries
import sqlite3

# Function to delete all entries from the database
def delete_all_entries(db_name='cam1.db'):
    # Connect to the database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Query to delete all rows from the vehicle_data table
    cursor.execute("DELETE FROM vehicle_data")

    # Commit the changes to the database
    conn.commit()

    print("All entries have been deleted from the database.")

    # Close the connection
    conn.close()

# Call the function to delete all entries
delete_all_entries()


# retrive all entries

"""import sqlite3

# Function to retrieve all data from the database
def get_all_entries(db_name='cam1.db'):
    # Connect to the database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Query to select all data from the vehicle_data table
    cursor.execute("SELECT * FROM vehicle_data")

    # Fetch all records
    records = cursor.fetchall()

    # Print each record
    for record in records:
        print(f"ID: {record[0]}, Entry Count: {record[1]}, Exit Count: {record[2]}, Entry Time: {record[3]}, Exit Time: {record[4]}")

    # Close the connection
    conn.close()

# Call the function to get all entries
get_all_entries()"""
