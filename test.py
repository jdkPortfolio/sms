# # # # import mysql.connector as mc
# # # # import time
# # # # from saving_transaction_data import obj

# # # # db = mc.connect(
# # # #     host = 'localhost',
# # # #     user = 'root',
# # # #     password = '',
# # # #     database = 'ms_db'
# # # # )

# # # # cursor = db.cursor()
# # # # sql = 'SELECT name, surname FROM client WHERE id = %s'
# # # # val = (1,)
# # # # cursor.execute(sql, val)

# # # # result = cursor.fetchall()
# # # # for i in result:
# # # #     print(i[0])
# # # # print(time.localtime())

# # # # # obj = data.Audit(1)
# # # # obj.transaction_deposits(80804020, 200)
# # # # True
# # # from cryptography.fernet import Fernet
 
# # # # we will be encryting the below string.
# # # message = "hello geeks"
 
# # # # generate a key for encryptio and decryption
# # # # You can use fernet to generate
# # # # the key or use random key generator
# # # # here I'm using fernet to generate key
 
# # # key = Fernet.generate_key()
 
# # # fernet = Fernet(key)

# # # encMessage = fernet.encrypt(message.encode())
# # # key_ = Fernet.generate_key()
 
# # # fernet = Fernet(key_)

# # # encMessage_ = fernet.encrypt(str(encMessage).encode())

# # # print(message)
# # # print(encMessage)
# # # print(encMessage_)

# # # # fernet = Fernet(key)
# # # decMessage = fernet.decrypt(encMessage_).decode()
# # # print("decrypted string: ", decMessage)
# # # temp = decMessage.encode()
# # # decMessage_ = fernet.decrypt(temp).decode()
# # # # fernet = Fernet(key)
# # # # decMessage_ = fernet.decrypt(bytes(decMessage, 'utf-8')).decode()



 
# # # print("decrypted string: ", decMessage)
# # # print("decrypted string: ", decMessage_)
# # # # print("original string: ", message)














# # # # print("key: ", key)
# # # # print("encrypted string: ", type(encMessage))
 
# # # # # decrypt the encrypted string with the
# # # # # Fernet instance of the key,
# # # # # that was used for encrypting the string
# # # # # encoded byte string is returned by decrypt method,
# # # # # so decode it to string with decode methods

# # from pathlib import Path

# # # Build paths inside the project like this: BASE_DIR / 'subdir'.
# # BASE_DIR = Path(__file__).resolve().parent.parent
# # print(BASE_DIR.joinpath('ui/templates'))

# # import smtplib

# # e = input("")
# # print(e.strip())
# # print(e)

# s = 'duncan'
# e = ''
# for i in range(0, len(s)):
#     e += s[len(s) - (i+1)]
# print(e)

import datetime as dt
# import bcrypt

# one = bcrypt
# two = bcrypt

# hashed = one.hashpw(b'password', bcrypt.gensalt(13))
# hasd = two.hashpw(b'password', bcrypt.gensalt(12))
# # print(bcrypt.checkpw(b'password', hasd))
# d = one.checkpw(b'password', hasd)
# print(d == False)

# import csv

# with open('report.csv', 'w', newline='') as file:
#     columns = ['Action', 'Invoked By', 'Date Invoked']
#     writer = csv.DictWriter(file, columns)

#     writer.writerow({'Action' : 'Action', 'Invoked By' : 'M', 'Date Invoked' : '2022-02-06'})

dt.datetime(year, month, day)