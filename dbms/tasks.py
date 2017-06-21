# Create your tasks here
from __future__ import absolute_import, unicode_literals
from aquila_v2.celery import app
from scripts import Inception
from scripts import functions
from model_model import models


@app.task()
def add(x, y):
    return x + y


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

