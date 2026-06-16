import sqlite3

conn = sqlite3.connect("transport.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM telemetry")

conn.commit()
conn.close()

print("Database cleared successfully")