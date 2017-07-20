import pymysql as pymysqldb
class DBAPI(object):
    def __init__(self, host, user, password, port, database):
        self.conn = pymysqldb.connect(host=host, user=user, passwd=password, port=int(port),
                                       database=database, autocommit=1, charset='utf8')
        self.conn.select_db(database)
        self.cur = self.conn.cursor()

    def conn_query(self, sql):
        try:
            rel = self.cur.execute(sql)
            result = self.cur.fetchall()
        except Exception as e:
            result = e
        return result

    def conn_dml(self, sql):
        try:
            rel = self.cur.execute(sql)
            if rel:
                pass
            else:
                return rel
        except Exception as e:
            return e

    def dml_commit(self):
        self.conn.commit()

    def dml_rollback(self):
        self.conn.rollback()

    def close(self):
        self.cur.close()
        self.conn.close()

import time
dbapi = DBAPI('192.168.1.180', 'root', 'root', 3306, 'shanjin')
while True:
    a = dbapi.conn_query('select * from performance_schema.replication_applier_status_by_worker')
    for items in a:
        error_code = items[5]
        if error_code == 1062:
            error_msg = items[6].split('table')[1].split(';')[0]
            error_id = items[6].split('table')[1].split('Duplicate entry')[1].split(' ')[1].strip('\'')
            sql = "delete from %s where id = %s" % (error_msg, error_id)
            dbapi.conn_query(sql)
            dbapi.conn_query("start slave")
        elif error_code == 1032:
            error_msg = items[6].split('table')[1].split(';')[0]
            print(error_msg)
    time.sleep(0.2)