# Create your tasks here
from __future__ import absolute_import, unicode_literals
from aquila_v2.celery import app
from scripts import Inception
from scripts import functions
from scripts import MyThreadPool
from model_model import models
import time

from model_model import models


@app.task()
def addx(x, y):
    ret = a(x, y)
    return ret


def a(x, y):
    time.sleep(5)
    print('sleep 5')
    return x * y


@app.task()
def mul(x, y):
    return x * y


@app.task()
def xsum(numbers):
    return sum(numbers)


@app.task()
def work_run_task(host, user, passwd, port, sql_content, wid):
    result_dict = {'data': {}}

    ince = Inception.Inception(db_host=host, db_user=user, db_passwd=passwd, db_port=port, sql_content=sql_content)
    run_result = ince.run_sql(1)
    result = functions.result_tran(run_result, result_dict)
    run_error_id = 1
    for items in result['data']:
        if result['data'][items]['status'] == '执行失败' or \
                        result['data'][items]['status'] == 'Error':
            run_error_id = 0
        elif result['data'][items]['status'] == '执行成功,备份失败':
            run_error_id = 5
        models.InceptionAuditDetail.objects.create(
            work_order_id=wid,
            sql_sid=items,
            flag=3,
            status=result['data'][items]['status'],
            error_msg=result['data'][items]['error_msg'],
            sql_content=result['data'][items]['sql'],
            aff_row=result['data'][items]['rows'],
            rollback_id=result['data'][items]['rollback_id'],
            backup_dbname=result['data'][items]['backup_dbname'],
            execute_time=int(float(result['data'][items]['execute_time']) * 1000),
            sql_hash=result['data'][items]['sql_hash']
        )

    models.InceptionWorkOrderInfo.objects.filter(work_order_id=wid).update(work_status=run_error_id)
    models.WorkOrderTask.objects.filter(work_order_id=wid).update(work_status=run_error_id)


def get_matedata(account_info):
    for item in account_info:
        host = item['host__host_ip']
        app_user = item['app_user']
        app_port = item['app_port']
        app_pass = item['app_pass']

        os_user = item['host__host_user']
        os_pass = item['host__host_pass']
        os_port = item['host__host_port']

        print(host, app_user, app_pass, app_port, os_pass, os_port, os_user)
        conn_info = GetMetadataitem(host=host, user=app_user, port=app_port, passwd=app_pass)
        conn_info.get_tables()


class GetMetadataitem(object):
    def __init__(self, host, user, port, passwd):
        self.host = host
        self.user = user
        self.port = int(port)
        self.passwd = passwd
        self.cur = ''

    def conn(self):
        db = functions.DBAPI(host=self.host, user=self.user, password=self.passwd, port=self.port)

        if db.error:
            models.GetMetaDataError.objects.create(host=self.host, error_msg=db.error)
        else:
            self.cur = db

    def get_tables(self):
        self.conn()
        sql = """SELECT table_schema, table_name, engine, row_format, table_rows, avg_row_length,
                   data_length, max_data_length, index_length, data_free, auto_increment,
                   table_collation, table_comment, create_time, update_time, check_time
            FROM information_schema.tables
            where table_schema not in ('sys', 'test', 'information_schema', 'performance_schema')"""
        if self.cur:
            result = self.cur.conn_query(sql)
            print(result)
        else:
            print(11111)

    def get_indexs(self):
        pass

    def get_columns(self):
        pass

    def get_rocedure(self):
        pass



"""
元数据信息：
1. 库
2. 表     information_schema.tabls
3. 列信息 information_schema.columns
3. 索引   information_schema.statistics
4. 存储过程 函数  information_schema.routines
5. 触发器    information_schema.events

存储过程 函数

schema_name,
trigger_name,
content,
create_time,
last_altered



选择机器列出库列表， 并不触发js
选择库， 列出所有的表、存储过程与函数信息， 触发第一个表的js，
    显示表的列信息
        SELECT table_name,
           column_name,
           column_type,
           collation_name,
           IS_NULLABLE,
           column_key,
           column_default,
           extra,
           PRIVILEGES,
           column_comment
        FROM information_schema.columns
        WHERE table_schema = 'aquila' AND table_name = 'dbms_workordertask';
    显示表的索引信息
        select
        table_schema,
        table_name,
        column_name,
        non_unique,
        index_name,
        seq_in_index, collation,
        cardinality,
        sub_part,
        packed, nullable, index_type, index_comment
        from information_schema.statistics where TABLE_SCHEMA='aquila' and TABLE_NAME='dbms_workordertask';
    显示表的基本信息
        SELECT
            table_schema,
            table_name,
           engine,
           row_format,
           table_rows,
           avg_row_length,
           data_length,
           max_data_length,
           index_length,
           data_free,
           auto_increment,
           table_collation,
           table_comment,
           create_time,
           update_time,
           check_time
        FROM information_schema.tables
        WHERE table_schema = 'aquila' AND table_name = 'dbms_workordertask';
=======

    models.InceptionWorkOrderInfo.objects.filter(work_order_id=wid).update(work_status=run_error_id)
    models.WorkOrderTask.objects.filter(work_order_id=wid).update(work_status=run_error_id)
>>>>>>> de10c29c9cc4e0a155f9c46b9483963707c6543e

    显示表的建表语句
"""