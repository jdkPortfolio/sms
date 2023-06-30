from config import cursor, db
import time
import csv

class Audit:
    def __init__(self, id):
        self.id = id
    
    
    def moneyTrail(self, account_num, amount, action):
        query = "INSERT into moneytrail (action, account_num, amount, operator) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (action, account_num, amount, self.id, ))
        db.commit()

    def actionTrail(self, action):
        query = "INSERT into actiontrail (action, operator, created_at) VALUES (%s, %s, NOW())"
        cursor.execute(query, (action, self.id, ))
        db.commit()

    def actionReport(self, sdt, edt):
        query = '''select aa.description, concat(u.name, ' ', u.surname) as name, a.created_at
            from users u
            inner join actiontrail a on u.id = a.operator
            inner join actions aa on a.action = aa.id
            where a.created_at between %s and %s
            group by a.created_at
        '''
        cursor.execute(query, (sdt, edt, ))
        result = cursor.fetchall()

        file_name = 'AuditReport_'+str(time.localtime().tm_hour)+str(time.localtime().tm_min)+str(time.localtime().tm_sec)+str('.csv')
        with open(file_name, 'w', newline='') as file:
            columns = ['Action', 'Invoked By', 'Date Invoked']
            writer = csv.DictWriter(file, columns)
            for row in result:
                if row[0] == 'HashPW' or row[0] == 'CheckPW':
                    continue
                else:
                    writer.writerow({'Action' : row[0], 'Invoked By' : row[1], 'Date Invoked' : row[2]})


    


obj = Audit(27)
obj.actionReport('2022-02-04', '2022-02-07')

    







        
        
