#!/bin/env python3
# _*_ coding:utf8 _*_

from django.conf import settings
from django.core.exceptions import ValidationError
from multiprocessing import Process
from email.header import Header
from email.mime.text import MIMEText
import smtplib
import pymysql as pymysqldb
import paramiko
import socket
import struct
import re
import time
import hashlib
import json
import os
import logging


class DBAPI(object):
    def __init__(self, host, user, password, port, database=None):
        try:
            self.conn = pymysqldb.connect(host=host, user=user, passwd=password, port=int(port),
                                          autocommit=1, charset='utf8')
            if database:
                self.conn.select_db(database)
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

    def get_col(self):
        field_names = [i[0] for i in self.cur.description]
        return field_names

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


def result_tran(result, result_dict):
    for id, row in enumerate(result):
        result_dict['data'][id] = {}
        result_dict['data'][id]['sid'] = str(row[0])
        if row[3] == 'Audit completed' and row[2] == 0:
            msg = 'Successfully'
            msg_code=0
        elif row[3] == 'Audit completed' and row[2] == 1:
            msg = 'Warning'
            msg_code = 1
        elif row[3] == 'Audit completed' and row[2] == 2:
            msg = 'Error'
            msg_code = 2
        elif row[3] == 'Execute failed':
            msg = '执行失败'
            msg_code = 3
        elif row[3] == 'Execute Successfully':
            msg = '执行成功'
            msg_code = 4
        elif row[3] == 'Execute Successfully\nBackup successfully':
            msg = '执行成功,备份成功'
            msg_code = 5
        elif row[3] == 'Execute Successfully\nBackup filed':
            msg = '执行成功,备份失败'
            msg_code = 6
        else:
            msg = '审核完成'
            msg_code = 7

        a = ''
        for kxxxx, rows in enumerate(row[4].split('\n')):
            a = a + rows + '---'
        result_dict['data'][id]['status'] = msg
        result_dict['data'][id]['status_code'] = msg_code
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
    master_result = {'status': 1, 'data': ''}
    if db.error:
        master_result['staus'] = 0
        master_result['data'] = db.error
        return master_result
    ret = db.conn_query('show slave status')
    if len(ret):
        master_result['data'] = ret[0][1]
    else:
        master_result['data'] = db_ip
    return master_result


class SplitSql(object):
    def __init__(self, task_type, sql):
        """
        :param task_type: 1: explain, 2: select, 3: audit
        :param sql: to be checked SQL content
        """
        self.task_type = task_type
        self.sql = sql
        self.check_all_flag = True
        self.sql_check_result_dict = {'status': False, 'sql': self.sql}
        self.sql_content_list = self.sql.lower().split(';')

    def get_audit(self):
        self.check_all()
        if not self.check_all_flag:
            return self.sql_check_result_dict
        audit_dict = {'ddl': 0, 'dml': 0}
        ddl_sql_list = ['alter', 'create']
        dml_sql_list = ['insert', 'update', 'delete']
        for row in self.sql_content_list[:-1]:
            for dml in dml_sql_list:
                flag = re.search(r'^{0}$'.format(dml), row.split()[0])
                if flag:
                    audit_dict['dml'] = 1
            for ddl in ddl_sql_list:
                flag = re.search(r'^{0}$'.format(ddl), row.split()[0])
                if flag:
                    audit_dict['ddl'] = 1
        if audit_dict['ddl'] == audit_dict['dml'] and audit_dict['ddl'] == 1:
            pass
        else:
            self.sql_check_result_dict['status'] = True
        return self.sql_check_result_dict

    def sql_split(self):
        self.check_all()
        if not self.check_all_flag:
            return self.sql_check_result_dict

        if self.task_type == 1 or self.task_type == 2:
            frist_sql_content_list = self.sql_content_list[0].split()
            if self.task_type == 1:
                if frist_sql_content_list[0] == 'explain':
                    if frist_sql_content_list[1] == 'select' or frist_sql_content_list[1] == 'update':
                        self.sql_check_result_dict['status'] = True
                elif frist_sql_content_list[0] == 'select':
                    self.sql_check_result_dict['status'] = True
            elif frist_sql_content_list[0] == 'select':
                for item in frist_sql_content_list:
                    into_status = re.search(r'^into$', item)
                    if into_status:
                        self.sql_check_result_dict['status'] = False
                        break
                    else:
                        self.sql_check_result_dict['status'] = True
            return self.sql_check_result_dict
        else:
            self.get_audit()

    def check_all(self):
        sql_content_list = self.sql.lower().split()
        error_list = ['begin', 'set', 'commit', 'rollback', 'revoke', 'rename', 'use'
                      'grant', '\*', 'execute', 'flush', 'shutdown', 'change', 'call']
        for item in sql_content_list:
            for i in error_list:
                flag = re.search(r'^{0}$'.format(i), item)
                if flag:
                    self.check_all_flag = False
                    break


class Logger(object):
    __instance = None

    def __init__(self):
        self.run_log_file = settings.RUN_LOG_FILE
        self.error_log_file = settings.ERROR_LOG_FILE
        self.run_logger = None
        self.error_logger = None

        self.initialize_run_log()
        self.initialize_error_log()

    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = object.__new__(cls, *args, **kwargs)
        return cls.__instance

    @staticmethod
    def check_path_exist(log_abs_file):
        log_path = os.path.split(log_abs_file)[0]
        if not os.path.exists(log_path):
            os.mkdir(log_path)

    def initialize_run_log(self):
        self.check_path_exist(self.run_log_file)
        file_1_1 = logging.FileHandler(self.run_log_file, 'a', encoding='utf-8')
        fmt = logging.Formatter(fmt="%(asctime)s - %(levelname)s :  %(message)s")
        file_1_1.setFormatter(fmt)
        logger1 = logging.Logger('run_log', level=logging.INFO)
        logger1.addHandler(file_1_1)
        self.run_logger = logger1

    def initialize_error_log(self):
        self.check_path_exist(self.error_log_file)
        file_1_1 = logging.FileHandler(self.error_log_file, 'a', encoding='utf-8')
        fmt = logging.Formatter(fmt="%(asctime)s  - %(levelname)s :  %(message)s")
        file_1_1.setFormatter(fmt)
        logger1 = logging.Logger('run_log', level=logging.ERROR)
        logger1.addHandler(file_1_1)
        self.error_logger = logger1

    def log(self, message, mode=True):
        """
        写入日志 Logger().log(str(response), False)
        :param message: 日志信息
        :param mode: True表示运行信息，False表示错误信息
        :return:
        """
        if mode:
            self.run_logger.info(message)
        else:
            self.error_logger.error(message)


class MailSender(object):
    def __init__(self):
        self.mail_server = settings.EMAIL['SERVER']
        self.mail_ssl_port = int(settings.EMAIL['SSL_PORT'])
        self.mail_form_user = settings.EMAIL['FROM_ADDRESS']
        self.mail_passwd = settings.EMAIL['PASSWORD']

    def _send(self, title, content, to_address):
        msg = MIMEText(content)
        msg['From'] = self.mail_form_user
        msg['To'] = ','.join(to_address)
        msg['Subject'] = Header(title, "utf-8").encode()
        server = smtplib.SMTP_SSL(self.mail_server, self.mail_ssl_port)
        server.login(self.mail_form_user, self.mail_passwd)
        server.sendmail(self.mail_form_user, to_address, msg.as_string())
        server.quit()

    def send_email(self, title, content, to_address):
        p = Process(target=self._send, args=(title, content, to_address))
        p.start()