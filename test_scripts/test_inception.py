import pymysql
sql="inception get osc processlist;"
try:
    conn=pymysql.connect(host='192.168.1.6', user='', passwd='', db='', port=6669)
    cur=conn.cursor()
    ret=cur.execute(sql)
    result=cur.fetchall()
    num_fields = len(cur.description)
    for line in result[0]:
        print(line)
    field_names = [i[0] for i in cur.description]
    # for row in result:
    #     print(row[0], "|",row[1],"|",row[2],"|",row[3],"|",row[4],"|",
    #     row[5],"|",row[6],"|",row[7],"|",row[8],"|",row[9],"|",row[10])
    cur.close()
    conn.close()
except Exception as e:
     print("Mysql Error %d: %s" % (e.args[0], e.args[1]))