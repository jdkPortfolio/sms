from main import User
from config import cursor, db
from audit import Audit

class Operations(User):
    def __init__(self, id, user, password, audit_obj):
        User.__init__(self, id, user, password, audit_obj)
        # Audit.__init__(self, id)

    def make_purchase(self, value):
        action = 3
        cost = 100
        charge = 10
        query = '''SELECT a.account_num, a.balance 
            FROM client c 
            INNER JOIN accounts a ON c.id = a.id 
            INNER JOIN userplates u ON c.id = u.user_id 
            WHERE u.plate_number = %s '''
        cursor.execute(query, (value, ))
        result = cursor.fetchall()
        print(result)
        for row in result:
            if row[1] > (cost+charge):
                new_bal = (row[1] - (cost+charge))
                cursor.execute("UPDATE accounts SET balance = %s WHERE account_num = %s", (new_bal, row[0], ))
                db.commit()
                print('Success')
                self.audit_obj.moneytTrail(row[0], (cost+charge), action)
                self.audit_obj.actionTrail(action)
                print('Success')
                return
        print(False)
        

# obj0 = Operations()
obj0 = Operations(27, 'qwerty', 'qwerty', Audit(27))
obj0.addLicensePlate('vaue')
obj0.make_purchase('value')

