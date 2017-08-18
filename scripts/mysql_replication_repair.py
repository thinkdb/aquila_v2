#!/bin/python3
"""
作者：
    think，现任 O盟 MySQL DBA
联系方式：
    qq: 996846239
功能：
    解决 MySQL Replication 的 1032 和 1062 错误
使用与依赖说明：
    1. 需要安装 pymysql, paramiko 模块
    2. 直接运行代码即可
    3. 运行后，在当前目录会生成一个日志文件(repair.log)，记录处理时的 sql 语句
        1). 重复数据错误时，会记录在从库删除的完整数据行
        2). 记录不存在的错误， 会记录在从库上插入的完整数据行
    4. binlog_row_image参数必须为full，不然会出错
注意事项:
    1. 只处理一次 1062 或者 1032 错误，想要多次执行， 再需要修改 main() 函数实现
    2. binlog_file_path 变量，最后必须有个 /, 不然无法修复， 或者 自己去改源码

    3. 如果想使用 python2 运行， 修改如下内容
        1). 把 pymysql 改成 MySQLdb
        2). 删除 Dbapi.__init__ 里面的 autocommit=1 参数
        3). 如果服务器设置了 autocommit=0, 则需要把227和314 的注释打开
    
    4. 如果表结构发生变化，请先修改表结构后再使用此脚本
    5. 如果主从中断后，主库操作表，之后又删除表的话。为了避免这种情况修复时报错，把获取表结构的信息由主库改成了从库

最好的 MySQL 培训机构：
    知数堂：http://zhishutang.com
"""

import pymysql
import logging
import paramiko
import time
import os
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

# 这边为所有需要的参数， 字典可有可无
slave_host = slave['host']
slave_user = slave['user']
slave_port = slave['port']
slave_password = slave['password']

master_host = master['host']
master_user = master['user']
master_port = master['port']
master_password = master['password']
master_ssh_user = master['ssh_user']
master_ssh_pass = master['ssh_pass']
master_mysqlbinlog_cmd = master['mysqlbinlog_cmd']
master_binlog_file_path = master['binlog_file_path']


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


def get_table_structure(slave_conn, table_name):
    # host = master_host
    # user = master_user
    # port = master_port
    # password = master_password

    # master_conn = Dbapi(host=host, user=user, port=port, password=password)
    result = slave_conn.conn_query('show create table {table_name}'.format(table_name=table_name))
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


def split_sql(recode_list, col_info):
    num = len(col_info)
    sql_file = []
    id = 0
    for item in recode_list[1:]:
        item = item.strip('### ')
        if id <= num:
            if re.search("^@", item):
                if "TIMESTAMP" in item:
                    sub_after_line = item.split("/*")[0].strip().split("=")[1]
                    data_timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(sub_after_line)))
                    item = item.split("/*")[0].strip().split("=")[0] + "=\'" + data_timestamp + "\'"
                else:
                    item = item.split("/*")[0].strip()

                if re.search("^@1", item):
                    if re.search('@1=NULL', item):
                        b = re.sub("=NULL", ' IS NULL', item)
                        a = re.sub("^@1", col_info[id], b)
                    else:
                        a = re.sub("^@1", col_info[id], item)

                else:
                    if re.search('@[\d]+=NULL', item):
                        b = re.sub("=NULL", ' IS NULL', item)
                        a = re.sub("^@[\d]+", ' and ' + col_info[id], b)
                    else:
                        a = re.sub("^@[\d]+", ' and ' + col_info[id], item)
                if a:
                    id += 1
                    sql_file.append(a)
                else:
                    id = 0
                    sql_file.append(item)
            else:
                id = 0
                sql_file.append(item)
    return sql_file


def find_recode_from_binlog(event, table_name, result):
    table_map_flag = 0
    event_flag = 0
    where_flag = 1
    option_flag = 0
    option_keyword = '### ' + event.split('_')[0].upper()
    new_table_name = '`{schema_name}`.`{table_name}`'.format(schema_name=table_name.split('.')[0],
                                                             table_name=table_name.split('.')[1])
    recode_list = []

    for line in result:

        if line.startswith('#') and re.search("Table_map", line) and re.search(new_table_name, line):
            table_map_flag = 1
        if line.startswith('#') and re.search(event, line):
            event_flag = 1
        if re.search('WHERE', line):
            where_flag = 1
        if line.startswith(option_keyword):
            recode_list.append('---line---')
            option_flag = 1
        if line.startswith('### SET'):
            where_flag = 0
            continue
        if line.startswith('###') and table_map_flag and event_flag and where_flag and option_flag:
            recode_list.append(line.strip())
    recode_list.append('---line---')
    return recode_list


def repair_1062(slave_conn, split_msg, slave_host_port):
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
    select_sql = 'select * from ' + split_msg['table_name'] + where_sql + ';'
    run_sql = slave_host_port + ' -- run SQL: ' + delete_sql
    logger('warning', run_sql)
    select_result = slave_conn.conn_query(select_sql)
    delete_recode = slave_host_port + ' Error_code: 1062 -- delete recode: ' + str(select_result)
    logger('warning', delete_recode)
    slave_conn.conn_dml(delete_sql)
    # slave_conn.dml_commit()
    slave_conn.conn_dml('start slave;')


def repair_1032(slave_conn, split_msg, master_log_file, start_log_pos, slave_host_port):
    end_pos = split_msg['end_log_pos']
    ssh_cmd = '{cmd} -vv --base64-output=decode-rows {master_file} ' \
              ' --start-position={start_pos}' \
              ' --stop-position={stop_pos}'.format(master_file=master_binlog_file_path + master_log_file,
                                                   cmd=master_mysqlbinlog_cmd,
                                                   start_pos=start_log_pos,
                                                   stop_pos=end_pos)

    host = master_host
    user = master_ssh_user
    passwd = master_ssh_pass
    result = ssh_run_cmd(host, user, passwd, ssh_cmd)
    event = split_msg['event']
    table_name = split_msg['table_name']

    col_info = get_table_structure(slave_conn, table_name)

    recode_list = find_recode_from_binlog(event, table_name, result)
    split_sql_list = split_sql(recode_list, col_info)
    ret = create_sql(split_sql_list)

    for sql in ret:
        if event == "Delete_rows":
            select_sql = sql.replace('DELETE', 'SELECT 1')
        else:
            select_sql = sql.replace('UPDATE', 'SELECT 1 from ')
        result = slave_conn.conn_query(select_sql)
        if not result:
            insert_sql = delete_or_update_to_insert(sql)
            run_sql = slave_host_port + ' Error_code: 1032 -- run SQL: ' + insert_sql
            logger('warning', run_sql)
            slave_conn.conn_dml(insert_sql)
            # slave_conn.dml_commit()
            slave_conn.conn_dml('start slave;')


def delete_or_update_to_insert(delete_sql):
    sql_1 = delete_sql.strip().replace('WHERE', 'VALUES(')
    sql_2 = sql_1.replace('and', ',')
    sql_3 = re.sub(' (\w)+=', ' ', sql_2)
    sql_4 = re.sub(';', ');', sql_3)
    sql_5 = re.sub('DELETE FROM|UPDATE', 'INSERT INTO', sql_4)
    run_sql = re.sub(', (\w)+ IS NULL ,', ', NULL ,', sql_5)
    return run_sql


def create_sql(split_sql_list):
    run_sql = ''
    for item in split_sql_list:
        if item == '---line---':
            run_sql += ';'
            yield run_sql
            run_sql = ''
        else:
            run_sql += ' ' + item


def repair_option(slave_conn, err_code, err_msg, master_log_file, start_log_pos, slave_host_port):
    if err_code in (1062, 1032):
        split_msg = split_err_msg(err_code, err_msg)

        if err_code == 1062:
            repair_1062(slave_conn, split_msg, slave_host_port)

        if err_code == 1032:
            repair_1032(slave_conn, split_msg, master_log_file, start_log_pos, slave_host_port)

    # 其他的错误可以在这边加入


def main():
    slave_host_port = slave_host + ':' + str(slave_port)

    # 多次执行时，将下面代码加入循环中即可
    slave_conn = Dbapi(host=slave_host,
                       user=slave_user,
                       port=slave_port,
                       password=slave_password)
    ret = slave_conn.conn_query('show slave status;')[0]
    if ret[11] == 'No':
        err_code = ret[18]
        err_msg = ret[19]
        master_log_file = ret[9]
        start_log_pos = ret[21]

        repair_option(slave_conn, err_code, err_msg, master_log_file, start_log_pos, slave_host_port)


if __name__ == '__main__':
    main()
