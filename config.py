import mysql.connector as mc
from cryptography.fernet import Fernet

db = mc.connect(
    host = 'localhost',
    user = 'root',
    password = 'J1276r+d',
    database = 'ms_db'
)

cursor = db.cursor()
# sql = 'SELECT * FROM client'
# cursor.execute(sql)

# result = cursor.fetchall()
# print(result)