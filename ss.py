import sqlite3

# Function to fetch and print the data from the personal_info table
def print_database():
    # Connect to the SQLite database
    conn = sqlite3.connect('personal_info.db')
    cursor = conn.cursor()

    # Query the personal_info table
    cursor.execute("SELECT key, value FROM personal_info")

    # Fetch all rows
    results = cursor.fetchall()

    # Print the results
    print("Current values in the personal_info table:")
    for row in results:
        print(f"{row[0]}: {row[1]}")

    # Close the database connection
    conn.close()

# Call the function to print the database values
print_database()
