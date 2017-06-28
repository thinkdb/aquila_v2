from django.shortcuts import render, redirect
from django.views import View
from model_model import models
from back.views.AuthAccount import AuthAccount, GetUserInfo
from django.utils.decorators import method_decorator
from scripts import functions
from django.conf import settings


@method_decorator(AuthAccount, name='dispatch')
class RollBack(View):
    def get(self, request, wid):
        rollback_host = settings.INCEPTION['backup']['BACKUP_HOST']
        rollback_port = int(settings.INCEPTION['backup']['BACKUP_PORT'])
        rollback_passwd = settings.INCEPTION['backup']['BACKUP_PASSWORD']
        rollback_user = settings.INCEPTION['backup']['BACKUP_USER']
        rollback_info = []
        # 同一个工单有多个sql语句被执行
        rollback = models.InceptionAuditDetail.objects.filter(work_order_id=wid,
                                                              flag=3).exclude(backup_dbname='None').all()

        rollback_conn = functions.DBAPI(host=rollback_host, user=rollback_user,
                                        port=rollback_port, password=rollback_passwd)
        # 同一个工单可能出现往多个库中操作表数据
        for line in rollback:
            # 循环每个db-name
            back_db_name = line.backup_dbname
            roll_back_id = line.rollback_id      # 回滚id 全局唯一

            get_table_name_sql = "select tablename from %s.`$_$Inception_backup_information$_$` where opid_time = %s" %\
                       (back_db_name, roll_back_id)

            tablename = rollback_conn.conn_query(sql=get_table_name_sql)

            # 循环多个table_name
            tname = tablename[0][0]
            rollback_sql = """
                          select a.sql_statement, b.rollback_statement FROM %s.`$_$Inception_backup_information$_$` a, %s.%s b
                          where a.opid_time = b.opid_time
                          and a.opid_time = %s """ % (back_db_name, back_db_name, tname, roll_back_id)
            # 每条语句对应的回滚语句
            rollback_statement = rollback_conn.conn_query(rollback_sql)

            if rollback_statement:
                roll_list = [wid, rollback_statement[0][0], rollback_statement[0][1]]
                rollback_info.append(roll_list)
            else:
                rollback_info = [[wid, '显示备份成功，可能因为表没有主键，server=[0|1], binlog_format=statement等问题导致备份失败', '']]
        return render(request, 'inception/RollBack.html', {'rollback_info': rollback_info})

    def post(self, request):
        pass