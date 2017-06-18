#!/bin/env python3
# _*_ coding:utf8 _*_

from django.conf import settings
from django.core.exceptions import ValidationError
import pymysql as pymysqldb
import paramiko
import socket
import struct
import re
import time
import hashlib
import json


class DBAPI(object):
    def __init__(self, host, user, password, port, database='test'):
        try:
            self.conn = pymysqldb.connect(host=host, user=user, passwd=password, port=int(port),
                                       database=database, autocommit=1, charset='utf8')

            #self.conn.select_db(database)
            self.cur = self.conn.cursor()
            self.error = None
        except Exception as e:
            self.error = e
            self._error()

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

    def _error(self):
        if self.error:
            return self.error


class FtpServer(object):
    def __init__(self, ip, user_name, passwd, port, comm=0, local_files=0, remote_files=0):
        self.host = ip
        self.user_name = user_name
        self.passwd = passwd
        self.port = port
        self.comm = comm
        self.local_files = local_files
        self.remote_files = remote_files

    # put the files
    def putfiles(self):
        t = paramiko.Transport(self.host, self.port)
        t.connect(username=self.user_name, password=self.passwd)
        sftp = paramiko.SFTPClient.from_transport(t)
        remotepath = self.remote_files
        localpath = self.local_files
        sftp.put(localpath, remotepath)
        t.close()

    # get the files
    def getfiles(self):
        t = paramiko.Transport(self.host, self.port)
        t.connect(username=self.user_name, password=self.passwd)
        sftp = paramiko.SFTPClient.from_transport(t)
        remotepath = self.remote_files
        localpath = self.local_files
        sftp.get(remotepath, localpath)
        t.close()


class OpSession(object):
    def login(self, request, username, flag=0):
        request.session['username'] = username
        request.session['is_login'] = True
        if flag:
            request.session.set_expiry(1209600)

    def logout(self, request):
        request.session.clear()

    def check_login(self, request, username):
        flag = request.session.get(username, None)
        if not flag:
            return False


class JsonCustomEncoder(json.JSONEncoder):
    def default(self, field):
        if isinstance(field, ValidationError):
            return {'code': field.code, 'messages': field.messages}
        else:
            return json.JSONEncoder.default(self, field)


def get_uuid():
    """
    Generate unique work order number
    """
    import random
    st = int(time.time() * 1000)
    i = random.randrange(100000, 999999)
    return int(str(st)+str(i))


def get_ip():
    """
    Get IP address
    """
    ip = socket.gethostbyname_ex(socket.gethostname())[2][0]
    aid = re.sub('\.', '_', ip)
    return aid


def num2ip(arg, int_ip):
    """
    IP address and number conversion
    arg == ip, Convert digital to IP address
    """
    if arg == 'ip':
        ip = socket.inet_ntoa(struct.pack('I', socket.htonl(int_ip)))
    else:
        ip = str(socket.ntohl(struct.unpack('I', socket.inet_aton(int_ip))[0]))
    return ip


def py_password(argv):
    """
    Generate an encrypted string
    """
    encrypt_key = getattr(settings, 'USER_ENCRYPT_KEY')
    h = hashlib.md5(bytes(encrypt_key, encoding="utf-8"))
    h.update(bytes(argv, encoding="utf-8"))
    pass_str = h.hexdigest()
    return pass_str


def get_config():
    flag = hasattr(settings, 'INCEPTION')
    if flag:
        incepiton_cnf = getattr(settings, 'INCEPTION')
        return incepiton_cnf


def tran_audit_result(result):
    result_dict = {}
    for i, items in enumerate(result):
        keys = i+1
        result_dict[keys] = {'error_msg': {}}
        result_dict[keys]['sql_sid'] = items[0]
        result_dict[keys]['status'] = items[1]
        result_dict[keys]['err_id'] = items[2]
        result_dict[keys]['stage_status'] = items[3]
        result_dict[keys]['sql_content'] = items[5]
        result_dict[keys]['aff_row'] = items[6]
        result_dict[keys]['rollback_id'] = items[7]
        result_dict[keys]['backup_dbname'] = items[8]
        result_dict[keys]['execute_time'] = items[9]
        result_dict[keys]['sql_hash'] = items[10]

        error_result = items[4]
        if error_result != 'None':

            result_dict[keys]['error_msg'] = {'error_msgs': {}}
            a = ''
            for id, rows in enumerate(error_result.split('\n')):
                result_dict[keys]['error_msg']['status'] = 1
                a = a+rows+'---'
            result_dict[keys]['error_msg']['error_msgs'] = a
        else:
            result_dict[keys]['error_msg']['status'] = 0
    return result_dict


def result_tran(result, result_dict):
    for id, row in enumerate(result):
        result_dict['data'][id] = {}
        result_dict['data'][id]['sid'] = str(row[0])

        if row[3] == 'Audit completed' and row[2] == 0:
            msg = '审核成功'
        elif row[3] == 'Audit completed' and row[2] == 1:
            msg = '警告'
        elif row[3] == 'Audit completed' and row[2] == 1:
            msg = '审核错误'
        elif row[3] == 'Execute failed':
            msg = '执行失败'
        elif row[3] == 'Execute Successfully':
            msg = '执行成功'
        elif row[3] == 'Execute Successfully\nBackup successfully':
            msg = '执行成功,备份成功'
        elif row[3] == 'Execute Successfully\nBackup filed':
            msg = '执行成功,备份失败'
        else:
            msg = '未知状态'

        a = ''
        for kxxxx, rows in enumerate(row[4].split('\n')):
            a = a + rows + '---'
        result_dict['data'][id]['status'] = msg
        result_dict['data'][id]['error_msg'] = a
        result_dict['data'][id]['sql'] = row[5]
        result_dict['data'][id]['rows'] = row[6]
        result_dict['data'][id]['rollback_id'] = row[7]
        result_dict['data'][id]['backup_dbname'] = row[8]
        result_dict['data'][id]['execute_time'] = row[9]
        result_dict['data'][id]['sql_hash'] = '----' if len(row[10]) == 0 else row[10]
    return result_dict


def get_master(db_ip, app_user, app_pass, app_port, database):
    db = DBAPI(db_ip, app_user, app_pass, app_port, database)

    if db.error:
        return db.error
    ret = db.conn_query('show slave status')
    if len(ret):
        master = ret[0][1]
    else:
        master = db_ip
    return master


sql = "explain select session_key from django_session"


def GetFristSqlStatus(sql_content):
    illegality_dict = {'sql': '', 'status': True}
    frist_sql = sql_content.lower().split(';')[0]
    sql_content_list = frist_sql.split()
    for item in sql_content_list:
        r = re.search('insert|delete|update|alter|drop|begin|set|commit|rollback|revoke|'
                      'grant|\*|execute|flush|shutdown|change', item)
        if r:
            illegality_dict['status'] = False
            return illegality_dict
    illegality_dict['sql'] = frist_sql
    return illegality_dict


a = GetFristSqlStatus(sql_content=sql)

if a['status'] == True:
    sql = a['sql']

# db = DBAPI(host='192.168.1.6', user='select_user', password='select_privi', port=3306, database='aquila')
# result = db.conn_query(sql)
# if isinstance(result, pymysqldb.err.ProgrammingError):
#     print(str(result).split(',')[1].strip(')'))
# else:
#     for item in result:
#         print(item)