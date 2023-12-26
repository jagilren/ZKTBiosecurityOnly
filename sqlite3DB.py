import sqlite3
import os

database_file = 'my_database.db'

# Check if the database file already exists
if not os.path.exists(database_file):
    # If the database doesn't exist, create it and connect
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()

    # Create the "Controladoras" table
    cursor.execute('''
        CREATE TABLE Controladoras (
            NAME TEXT PRIMARY KEY,
            IP TEXT,
            SN TEXT
        )
    ''')

    # Create the "DoorsControl" table with a foreign key reference to "Controladoras"
    cursor.execute('''
        CREATE TABLE DoorsControl (
            Name TEXT,
            Door TEXT,
            FOREIGN KEY (Name) REFERENCES Controladoras(NAME)
        )
    ''')

    # Commit the changes and close the connection
    conn.commit()
    conn.close()
else:
    # If the database already exists, just connect to it
    conn = sqlite3.connect(database_file)
    cursor = conn.cursor()

# Perform other operations with the database as needed

# Close the connection when done
conn.close()
