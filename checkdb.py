import sqlite3

# Connect to database
conn = sqlite3.connect("leave.db")

# Create cursor
cursor = conn.cursor()

# Show tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
print("Tables:", cursor.fetchall())

# Fetch leaves
print("\n--- LEAVES TABLE ---")
cursor.execute("SELECT * FROM leaves")
rows = cursor.fetchall()

for row in rows:
    print(row)

# Fetch users
print("\n--- USERS TABLE ---")
cursor.execute("SELECT * FROM users")
rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()