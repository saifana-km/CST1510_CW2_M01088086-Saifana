import sqlite3

# Connect to database 
conn = sqlite3.connect('DATA/intelligence_platform.db') 
cursor = conn.cursor()
 
# Create table 
cursor.execute(""" CREATE TABLE IF NOT EXISTS users ( 
id INTEGER PRIMARY KEY AUTOINCREMENT, 
username TEXT NOT NULL UNIQUE, 
password_hash TEXT NOT NULL, 
role TEXT DEFAULT 'user' ) """) 

# Save changes 
conn.commit()
