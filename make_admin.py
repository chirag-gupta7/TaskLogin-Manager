import sqlite3

conn = sqlite3.connect("tasklogin.db")
cursor = conn.cursor()

cursor.execute("UPDATE users SET role = 'admin' WHERE username = ?", ("random",))

conn.commit()
conn.close()

print("Done — user updated to admin.")