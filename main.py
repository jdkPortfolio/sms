import random
from audit import Audit
from config import cursor, db
from cryptography.fernet import Fernet
import datetime as dt
from smtplib import SMTP
import bcrypt

class Encrypt:
    def __init__(self, id, plain, access, encrypted):
        self.id = id
        self.plain = plain
        self.access = access
        self.encrypted = encrypted
        
    def encrypt(self):
        self.encrypted = bcrypt.hashpw(bytes(self.plain, 'utf-8'), bcrypt.gensalt(12))

    def decrypt(self):
        self.access = bcrypt.checkpw(bytes(self.plain, 'utf-8'), bytes(self.encrypted, 'utf-8'))
    
    def password_change(self):
        self.encrypt()
        cursor.execute("UPDATE users SET password = %s WHERE id = %s", (self.encrypted, self.id, ))
        db.commit()



class User:
    def __init__(self, id, user, password, audit_obj):
        self.id = id
        self.user = user
        self.password = password
        self.audit_obj = audit_obj
        


    def register(self):
        name = input('Enter your name : \n')
        surname = input('Enter your surname : \n')
        dob = input('enter your dob(yyyy-mm-dd)\n')

        sql = "INSERT INTO users (name, surname, dob, username, password) VALUES (%s, %s, %s, %s, %s)"
        val = (name, surname, dob, self.user, self.password)
        cursor.execute(sql, val)
        db.commit()

        sql = "SELECT last_insert_id()"
        cursor.execute(sql)
        result = cursor.fetchall()
        self.id = result[0][0]
        self.audit_obj = Audit(self.id)
        self.audit_obj.actionTrail(1)
        self.create_account()


    def create_account(self):
        self.user = input('enter your username : \n')
        self.password = input('enter your password : \n')
        
        encrypt = Encrypt(self.id, self.password, '', '', )
        encrypt.encrypt()
        self.audit_obj.actionTrail(14)

        sql = "UPDATE users SET username = %s, password = %s, status = %s WHERE id = %s"
        val = (self.user, encrypt.encrypted, 1, self.id,)
        cursor.execute(sql, val)
        db.commit()

        sql = "INSERT INTO accounts (id) VALUES (%s)"
        val = (self.id,)
        cursor.execute(sql, val)
        db.commit()
        
        sql = "SELECT account_num FROM accounts WHERE id = %s"
        cursor.execute(sql, (self.id,) )
        account_num = cursor.fetchall()
        print('Account created...\nAccount Number : '+str(account_num[0][0])+'')
        self.audit_obj.actionTrail(2)
        user_menu()

        print('Account Creation Unsuccessful')
        menu()

    
        

    def login(self):
        sql = '''SELECT u.id, r.description, u.password 
            from users u
            inner join roles r on u.access_level = r.id 
            WHERE u.username = %s AND u.status = 1'''
        val = (self.user,)
        cursor.execute(sql, val)
        result = cursor.fetchall()
        for row in result:
            dec_obj = Encrypt(row[0], self.password, '', row[2])
            dec_obj.decrypt()
            if dec_obj.access == True:
                print('Login Successful')
                self.id = row[0]
                self.audit_obj = Audit(self.id)
                self.audit_obj.actionTrail(3)
                if row[1] == 'SuperUser':
                    self = Admin(self.id, self.user, self.password, self.audit_obj)
                    admin_menu(self)
                elif row[1] == 'Admin':
                    admin_menu()
                else:
                    user_menu()
        print('Username and or password wrong')

    
    def forgot_password(self):
        self.user = input('Enter Email Address: \n')
        code = random.randint(1000000, 9999999)
        print(code)
        #send code via email
        cursor.execute("INSERT INTO password_reset (username, code) VALUES (%s, %s)", (self.user, code, ))
        db.commit()

    
    def verification(self):
        code = input('Enter Verfication Code: \n')
        cursor.execute("SELECT code FROM password_reset WHERE username = %s", (self.user,))
        result = cursor.fetchall()
        for row in result:
            if code == row[0]:
                cursor.execute("UPDATE password_reset SET verified = %s", (1,))
                db.commit()
                self.password_reset()
            print('Incorect Code')
            self.verification()
        print('No code requested for this email')
        menu()

    def password_reset(self):
        self.password = input('Enter New Password: \n')
        conf_password = input('Confirm Password: \n')
        if self.password == conf_password:
            cursor.execute("SELECT id FROM users WHERE username = %s", (self.user, ))
            user_id = cursor.fetchall()
            self.id = user_id[0][0]
            obj = Encrypt(self.id, self.password, '', '')
            obj.password_change()
            self.audit_obj.actionTrail(12)
            self.login()
        self.password_reset()


    def check_account_num(self, account_num):
        
        cursor.execute("SELECT * from accounts WHERE account_num = %s", (account_num, ))
        result = cursor.fetchall()
        for row in result:
            cursor.execute("SELECT CONCAT(name,' ', surname) AS name from users WHERE id = %s", (row[0], ))
            name = cursor.fetchall()
            print("Confirm Transfer To Account Holder : "+str(name[0][0])+"\n1. Yes\n2. No")
            response = int(input())
            if response == 1:
                self.addContact(row[0])
                balance = int(row[1])
                self.transfer_doh(account_num, balance)
            elif response == 2:
                user_menu()
                
        print('Account number not found\n')
        user_menu()
    

    def transfer_doh(self, account_num, balance):
        amount = int(input('Enter amount to transfer to : '+str(account_num)+'\n'))
        password = input('Verify Your Password\n')
        if self.password == password:
            cursor.execute("SELECT balance from accounts WHERE id = %s", (self.id, ))
            result = cursor.fetchall()
            for row in result:
                if row[0] >= amount:
                    updated_balance = balance + amount
                    cursor.execute("UPDATE users SET balance = %s where account_num = %s",
                                (updated_balance, account_num))
                    db.commit()
                    print('Transfer Successful')
                    self.deduct_transfered_amount(amount)
                    self.audit_obj.actionTrail(1)
                    user_menu()
        print('Insufficient Balance to perfom transaction\n')
        user_menu()

    def deduct_transfered_amount(self, amount):
        
        cursor.execute("SELECT balance from users WHERE id = %s", (self.id, ))
        result = cursor.fetchall()
        for row in result:
            new_balance = int(row[0]) - amount
            cursor.execute("UPDATE users SET balance = %s where id = %s",
                        (new_balance, self.id))
            db.commit()
            print('New Balance is : '+str(new_balance))


    def balance(self):
        cursor.execute("SELECT balance from accounts where id = %s",
                            (self.id, ))
        result = cursor.fetchall()
        for row in result:
            print('Your Balance Equiry is : $'+str(row[0]))

    def addContact(self, cid):
        res = int(input("Save Account Number to Contacts\n1. Yes\n2. No\n"))
        if res == 1:
            cursor.execute("INSERT INTO contacts (contact_id, user_id) VALUES (%s, %s)", (cid, self.id, ))
            db.commit()
            print('Account Saved.')
        else:
            pass
    
    def showContacts(self):
        cursor.execute("SELECT id, contact_id FROM contacts WHERE user_id = %s", (self.id, ))
        contacts = cursor.fetchall()
        for row in contacts:
            cursor.execute("SELECT CONCAT(name, ' ', surname) AS name FROM users WHERE id = %s", (row[1], ))
            name = cursor.fetchall()
            print(str(row[0])+".", name[0][0])
    
    def transferToSavedAccount(self, cid):
        cursor.execute("SELECT account_num, balance FROM accounts WHERE user_id = %s", (cid, ))
        result = cursor.fetchall()
        for row in result:
            self.tranfer_doh(row[0], row[1])

    def addLicensePlate(self, value):
        cursor.execute("SELECT status FROM userplates WHERE user_id = %s AND plate_number = %s", (self.id, value, ))
        result = cursor.fetchall()
        message = ''
        for row in result:
            if row[0] == 1:
                message = 'Plate Already Active'
                return
            elif row[0] == 0:
                cursor.execute("UPDATE userplates SET status = %s WHERE user_id = %s", (1, self.id, ))
                db.commit()
                message = 'Plate Now Active'
                return
        cursor.execute("INSERT INTO userplates (user_id, plate_number, status, created_at) VALUES (%s, %s, %s, NOW())", (self.id, value, 1, ))
        db.commit()
        self.audit_obj.actionTrail(9)
        message = 'Plate Added. Staus : Active'

        print(message)

class Admin(User):
    def __init__(self, id, user, password, audit_obj):
        User.__init__(self, id, user, password, audit_obj)


    def deposit(self, account_num):
        amount = int(input('Enter Amount to be deposited\n'))
        cursor.execute("SELECT id, balance FROM accounts WHERE account_num = %s", (account_num, ))
        result = cursor.fetchall()
        for row in result:
            cursor.execute("SELECT CONCAT(name, ' ', surname) as name FROM users WHERE id = %s", (row[0], ))
            result_name = cursor.fetchall()
            response = int(input("Confirmation Deposit to Account Holder : "+str(result_name[0][0]+"\n1. Yes\n2. No\n")))
            if response == 1:
                updated_amount = int(row[1]) + amount
                cursor.execute("UPDATE accounts SET balance = %s where account_num = %s",
                            (updated_amount, account_num))
                db.commit()
                print('Amount deposited. New account balance : '+str(updated_amount))
                self.audit_obj.actionTrail(4)
                self.audit_obj.moneyTrail(account_num, amount, 4)
                admin_menu(self)
        print('Account Number not found')
          
        admin_menu(self)

    def withdraw(self, account_num):
        amount = int(input('Enter Amount to be withdrawn\n'))
        cursor.execute("SELECT id, balance from accounts WHERE account_num = %s", (account_num, ))
        result = cursor.fetchall()
        for row in result:
            cursor.execute("SELECT CONCAT(name, ' ', surname) as name FROM users WHERE id = %s", (row[0],))
            res_name = cursor.fetchall()
            response = int(input("Confirmation Withdraw from Account Holder : "+str(res_name[0][0]+"\n1. Yes\n2. No\n")))
            if response == 1 and row[1] >= amount:
                updated_amount = int(row[1]) - amount
                cursor.execute("UPDATE accounts SET balance = %s where id = %s",
                            (updated_amount, row[0]))
                db.commit()
                print('Amount withdrawn. New account balance : '+str(updated_amount))
                self.audit_obj.moneyTrail(account_num, amount, 5)
                self.audit_obj.actionTrail(5)
                admin_menu(self)
            elif response == 1 and row[1] < amount:
                print('Insufficient Balance\n')
                admin_menu(self)
            admin_menu(self)
        print('Account Number not found')
        admin_menu(self)
                    
    def display_one(self, account_num):
        cursor.execute("SELECT id from accounts where account_num = %s",
                            (account_num,))
        result = cursor.fetchall()
        for row in result:
            cursor.execute("SELECT CONCAT(name, ' ', surname) as name from users WHERE id = %s", (row[0], ))
            name = cursor.fetchall()
            for row in name:
                print('Account Holder Name : '+str(row[0]))

    def delete_account(self):
        status = 0
        cursor.execute("SELECT id, password FROM users WHERE username = %s", (self.user,))
        result = cursor.fetchall()
        for row in result:
            if self.password == row[1]:
                response = int(input("Confirmation To Delete Account(Action Can Not Be Reversed\n1. Yes\n2. No\n"))
                if response == 1:
                    cursor.execute("UPDATE users SET status = %s where id = %s",
                                (status, row[0], ))
                    db.commit()
                    print('Account deletion successful\n')
                    self.audit_obj.actionTrail(13)
                    menu(self)
                admin_menu(self)
        
        print('Error Deleting Account')
        admin_menu(self) 



def choose():
    account_num = int(input('Enter Account Number to View data\n'))
    # data.display_one(account_num)
    admin_menu()


def admin_menu(user_obj):
    print('''
        1.Deposit Money
        2.Withdraw Money
        3.Check User Accounts
        4.Delete Account
        8.Main Menu
        9.Exit
        ''')
    choice = int(input('Select option to proceed\n'))
    if choice == 1:
        account_num = int(input('Enter Account Number To Deposit into\n'))
        user_obj.deposit(account_num)
    elif choice == 2:
        account_num = int(input('Enter Account Number To Withdraw from\n'))
        user_obj.withdraw(account_num)
    elif choice == 3:
        account_num = int(input('Enter Account Number to View data\n'))
        user_obj.display_one(account_num)
        admin_menu(user_obj)
    elif choice == 4:
        print('Verify Credentials to delete account\n')
        user_obj.user = input('Enter account username\n')
        user_obj.password = input('Enter account password\n')
        user_obj.delete_account()
        admin_menu(user_obj)
    elif choice == 8:
        menu()
    elif choice == 9:
        exit()

user_obj = User('','','', '')           

def user_menu():
    print('''
        1.Transfer Money
        2.Balance Enquiry
        3.Main Menu
        4.Exit
        ''')
    select = int(input('Select option to proceed\n'))
    if select == 1:
        res = int(input('Transfer to Saved Accounts\n1. Yes\n2. No\n'))
        if res == 1:
            user_obj.showContacts()
            user_obj.transferToSavedAccount()
        else:
            account_num = int(input('Enter Account Number to Transfer to\n'))
            user_obj.check_account_num(account_num)#line 90
    elif select == 2:
        # user = input('Enter Username\n')
        # password = input('Enter Password\n')
        user_obj.balance()
        user_menu()
    elif select == 3:
        menu()#line 256
    elif select == 4:
        exit()
    else:
        print('Invalid Input')
        user_menu()

def menu(user_obj):
    print('''
        1.Register
        3.Login
        9.Exit
        ''')
    choice = int(input('Select option to proceed\n'))
    if choice == 1:
        user_obj.register()
    elif choice == 3:
        user_obj.user = 'start'
        user_obj.password = 'start'
        user_obj.login()
        menu(user_obj)
    elif choice == 9:
        exit()
    else:
        print('invalid input')
        menu()


# admin_obj = Admin('', '', '','')
menu(user_obj)

