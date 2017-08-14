#!/bin/python3
"""
功能：
    解决 MySQL Replication 的 1032 和 1062 错误
"""

import pymysql
import logging
import paramiko
import os
import time
import re

master = {
    'host': '192.168.1.5',
    'port': 3306,
    'user': 'root',
    'password': '123456',
    'ssh_user': 'mysql',
    'ssh_pass': 'mysql',
    'mysqlbinlog_cmd': '/usr/local/mysql/bin/mysqlbinlog',
    'binlog_file_path': '/mysqlData/'
}

slave = {
    'host': '192.168.1.4',
    'port': 3306,
    'user': 'root',
    'password': '123456'
}

BASE_DIR = os.path.dirname(__file__)


class Dbapi(object):
    def __init__(self, host, user, password, port, database=None):
        self.conn = pymysql.connect(host=host, user=user, passwd=password, port=int(port),
                                    database=database, autocommit=1, charset='utf8')
        if database:
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


def logger(log_level, msg):
    """
    日志记录功能
    """
    log = logging.getLogger(__name__)
    log.setLevel(logging.INFO)
    fh = logging.FileHandler(os.path.join(BASE_DIR, 'repair.log'), 'a', encoding='utf-8')
    fh.setLevel(logging.INFO)
    datefrm = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter("%(asctime)s - [%(levelname)s] %(message)s", datefrm)
    fh.setFormatter(formatter)
    log.addHandler(fh)
    log_flag = hasattr(log, log_level)
    if log_flag:
        level = getattr(log, log_level)
        level(msg)
    else:
        log.error("The logger module not find %s attribute...." % log_level)


def ssh_run_cmd(host, user, passwd, cmd, port=22):
    transport = paramiko.Transport(host, port)
    transport.connect(username=user, password=passwd)
    ssh = paramiko.SSHClient()
    ssh._transport = transport
    stdin, stdout, stderr = ssh.exec_command(cmd)
    ret = stdout.readlines()
    transport.close()
    return ret


def split_err_msg(err_code, err_msg):
    split_msg = {}
    table_name = err_msg.split('on table')[1].split(';')[0].strip()
    binlog_file = err_msg.split('master log')[1].split(',')[0].strip()
    end_log_pos = err_msg.split('master log')[1].split(',')[1].split()[1]
    event = err_msg.split('event')[0].split('execute')[1].strip()

    if err_code == 1062:
        dup_recode = err_msg.split('Duplicate entry')[1].split('for key')[0].strip().strip('\'')
        key_name = err_msg.split('Duplicate entry')[1].split('for key')[1].split(',')[0].strip().strip('\'')
        split_msg['dup_recode'] = dup_recode
        split_msg['index_name'] = key_name

    split_msg['table_name'] = table_name
    split_msg['binlog_file'] = binlog_file
    split_msg['end_log_pos'] = end_log_pos
    split_msg['event'] = event

    return split_msg


def get_table_structure(table_name):
    host = master['host']
    user = master['user']
    port = master['port']
    password = master['password']

    master_conn = Dbapi(host=host, user=user, port=port, password=password)
    result = master_conn.conn_query('show create table {table_name}'.format(table_name=table_name))
    col = get_column(result[0][1])
    return col


def get_column(data):
    col_num = 0
    col_list = []
    for item in data.split("\n")[1:]:
        col_re = re.search("^`", item.strip())
        if col_re:
            col_list.append(item.split()[0].strip("`"))
            col_num += 1
    col_list.append(col_num)
    return col_list


def convert_sql(recode_list, col_info):
    num = len(col_info)
    sql_file = []
    id = 0
    for item in recode_list:
        item = item.strip('### ')
        if id <= num:
            if re.search("^@", item):
                a = re.sub("^@[\d]+", col_info[id], item)
                if a:
                    id += 1
                    sql_file.append(a)
                else:
                    id = 0
                    sql_file.append(item)
            else:
                id = 0
                sql_file.append(item)

    print(sql_file)


def find_recode_from_binlog(event, table_name, result):
    table_map_flag = 0
    event_flag = 0
    new_table_name = '`{schema_name}`.`{table_name}`'.format(schema_name=table_name.split('.')[0],
                                                             table_name=table_name.split('.')[1])
    recode_list = []
    for line in result:
        if line.startswith('#') and re.search("Table_map", line) and re.search(new_table_name, line):
            table_map_flag = 1
        if line.startswith('#') and re.search(event, line):
            event_flag = 1

        if line.startswith('###') and table_map_flag and event_flag:
            recode_list.append(line)
        
    return recode_list


def repair_1062(slave_conn, split_msg, slave_host):
    where_sql = """ where 1=1"""
    # 这边处理 重复记录，可能是复合索引引起数据重复， 也可能是单列索引引起数据重复
    sql = """select distinct s.column_name, s.seq_in_index, c.data_type
                    from information_schema.columns c, information_schema.statistics s
                    where c.table_schema = s.table_schema
                    and c.table_name = s.table_name
                    and c.column_name = s.column_name
                    and c.table_schema='{schema_name}'
                    and c.table_name='{table_name}'
                    and s.index_name='{index_name}';""".format(schema_name=split_msg['table_name'].split('.')[0],
                                                               table_name=split_msg['table_name'].split('.')[1],
                                                               index_name=split_msg['index_name'])
    ret = slave_conn.conn_query(sql)
    for item in ret:
        data_type = item[2]

        # 处理非数值型数据 加 引号
        if data_type not in ('tintint', 'smallint', 'mediumint', 'int', 'bitint', 'float', 'double', 'decimal', 'bit'):
            where_sql += ' and ' + item[0] + '=\'' + split_msg['dup_recode'].split('-')[item[1] - 1] + '\''
        else:
            where_sql += ' and ' + item[0] + '=' + split_msg['dup_recode'].split('-')[item[1] - 1]
    delete_sql = 'delete from ' + split_msg['table_name'] + where_sql + ';'

    run_sql = slave_host + ' -- run SQL: ' + delete_sql
    logger('warning', run_sql)
    slave_conn.conn_dml(delete_sql)
    slave_conn.conn_dml('start slave;')


def repair_1032(slave_conn, split_msg, master_log_file, start_log_pos):
    end_pos = split_msg['end_log_pos']
    ssh_cmd = '{cmd} -v --base64-output=decode-rows {master_file} ' \
              ' --start-position={start_pos}' \
              ' --stop-position={stop_pos}'.format(master_file=master['binlog_file_path'] + master_log_file,
                                                   cmd=master['mysqlbinlog_cmd'],
                                                   start_pos=start_log_pos,
                                                   stop_pos=end_pos)

    host = master['host']
    user = master['ssh_user']
    passwd = master['ssh_pass']
    result = ssh_run_cmd(host, user, passwd, ssh_cmd)
    event = split_msg['event']
    table_name = split_msg['table_name']

    col_info = get_table_structure(table_name)

    recode_list = find_recode_from_binlog(event, table_name, result)
    convert_sql(recode_list, col_info, event)


def repair_option(slave_conn, err_code, err_msg, master_log_file, start_log_pos, slave_host):
    if err_code in (1062, 1032):
        split_msg = split_err_msg(err_code, err_msg)

        if err_code == 1062:
            repair_1062(slave_conn, split_msg, slave_host)

        if err_code == 1032:
            repair_1032(slave_conn, split_msg, master_log_file, start_log_pos)


def main():
    slave_host = slave['host'] + ':' + str(slave['port'])
    slave_conn = Dbapi(host=slave['host'],
                       user=slave['user'],
                       port=slave['port'],
                       password=slave['password'])
    ret = slave_conn.conn_query('show slave status;')[0]
    if ret[11] == 'No':
        err_code = ret[18]
        err_msg = ret[19]
        master_log_file = ret[9]
        start_log_pos = ret[21]

        repair_option(slave_conn, err_code, err_msg, master_log_file, start_log_pos, slave_host)


if __name__ == '__main__':
    main()
