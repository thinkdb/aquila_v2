from django.shortcuts import render, HttpResponse
from django.views import View
from model_model import models
from dbms import forms
from back.views.AuthAccount import AuthAccount, GetUserInfo
from django.utils.decorators import method_decorator
from scripts import functions
from scripts.functions import JsonCustomEncoder, get_uuid, result_tran
from scripts.Inception import Inception
import json, datetime


@method_decorator(AuthAccount, name='dispatch')
class SqlCommit(View):

    def __init__(self, **kwargs):
        super(SqlCommit, self).__init__(**kwargs)
        self.result_dict = {'data': {}, 'status': 0, 'error': '', 'running': 0, 'post_flag': 0}

    def get(self, request):
        user_info = GetUserInfo(request)
        obj = forms.SqlComForm()

        return render(request,
                      'inception/SqlCommit.html',
                      {'user_info': user_info,
                       'SqlComFormObj': obj,
                       'AuditResult': self.result_dict,
                       })

    def post(self, request):
        user_info = GetUserInfo(request)
        obj = forms.SqlComForm(request.POST)

        if obj.is_valid():
            self.result_dict['post_flag'] = 1
            self.result_dict['status'] = 1

            work_order_id = get_uuid()

            host_id = obj.cleaned_data['host']
            port = obj.cleaned_data['port']
            db_name = obj.cleaned_data['db_name']
            run_time = obj.cleaned_data['run_time']
            sql_content = 'use ' + db_name + ';' + obj.cleaned_data['sql_content']
            db_info = models.HostAPPAccount.objects.filter(host_id=host_id,
                                                           host__app_type__app_name='MySQL',
                                                           app_port=port
                                                           ).values('host__host_ip', 'app_user', 'app_pass')
            # auto audit sql
            db_host = db_info[0]['host__host_ip']
            db_user = db_info[0]['app_user']
            db_passwd = db_info[0]['app_pass']
            ince = Inception(db_host=db_host,
                             db_user=db_user,
                             db_passwd=db_passwd,
                             db_port=port,
                             sql_content=sql_content)
            result = ince.audit_sql()
            self.result_dict = result_tran(result, self.result_dict)

            if obj.cleaned_data['is_commit'] == '1':
                # commit audit sql
                self.result_dict['running'] = 1
                master_ip = functions.get_master(db_host, db_user, db_passwd, port, db_name)

                # InceptionWorkOrderInfo
                models.InceptionWorkOrderInfo.objects.create(
                    work_title=obj.cleaned_data['title'],
                    work_order_id=work_order_id,
                    work_user=user_info[0]['user_name'],
                    db_host=db_info[0]['host__host_ip'],
                    db_name=db_name,
                    master_host=master_ip,
                    review_user=obj.cleaned_data['review_name'],
                    work_run_time=datetime.datetime.now() if run_time == None else run_time
                )

                # InceptionAuditDetail
                for id in self.result_dict['data']:
                    models.InceptionAuditDetail.objects.create(
                        work_order_id=work_order_id,
                        sql_sid=id,
                        flag=1,
                        status=self.result_dict['data'][id]['status'],
                        error_msg=self.result_dict['data'][id]['error_msg'],
                        sql_content=self.result_dict['data'][id]['sql'],
                        aff_row=self.result_dict['data'][id]['rows'],
                        rollback_id=self.result_dict['data'][id]['rollback_id'],
                        backup_dbname=self.result_dict['data'][id]['backup_dbname'],
                        execute_time=self.result_dict['data'][id]['execute_time'],
                        sql_hash=self.result_dict['data'][id]['sql_hash'],
                        comm=obj.cleaned_data['comm']
                    )

                # InceAuditSQLContent
                models.InceAuditSQLContent.objects.create(
                    work_order_id=work_order_id,
                    sql_content=obj.cleaned_data['sql_content']
                )
                # WorkOrderTask
                # models.WorkOrderTask.objects.create(
                #     wid=work_order_id,
                #     host_ip=master_ip,
                #     app_user=db_user,
                #     app_pass=db_passwd,
                #     app_port=port,
                #     db_name=db_name
                # )
        else:
            self.result_dict['error'] = json.dumps(obj.errors)
        return render(request,
                      'inception/SqlCommit.html',
                      {'user_info': user_info,
                       'SqlComFormObj': obj,
                       'AuditResult': self.result_dict,
                       })


@method_decorator(AuthAccount, name='dispatch')
class SqlAudit(View):
    def get(self, request):
        user_info = GetUserInfo(request)
        """
         显示内容 (审核页面)
        1. 工单标题
        2. 工单id
        3. 发起人
        4. 发起时间
        5. 主库地址
        6. 工单说明
        """
        audit_sql_info = models.InceptionWorkOrderInfo.objects.filter(
            review_user=user_info[0]['userrolerelationship__role_id']).all()

        return render(request, 'inception/SqlAudit.html', {'user_info': user_info,
                                                           'audit_sql_info': audit_sql_info})

    def post(self, request):
        user_info = GetUserInfo(request)
        return render(request, 'HostGroupManage.html', {'user_info': user_info})


@method_decorator(AuthAccount, name='dispatch')
class SqlRunning(View):
    def get(self, request):
        user_info = GetUserInfo(request)
        return render(request, 'HostGroupManage.html', {'user_info': user_info})

    def post(self, request):
        pass


@method_decorator(AuthAccount, name='dispatch')
class SqlView(View):
    def get(self, request):
        user_info = GetUserInfo(request)
        return render(request, 'HostGroupManage.html', {'user_info': user_info})

    def post(self, request):
        user_info = GetUserInfo(request)
        return render(request, 'HostGroupManage.html', {'user_info': user_info})


@method_decorator(AuthAccount, name='dispatch')
class SqlDetail(View):
    def get(self, request, wid):
        user_info = GetUserInfo(request)
        return render(request, 'HostGroupManage.html', {'user_info': user_info})

    def post(self, request, wid):
        user_info = GetUserInfo(request)
        return render(request, 'HostGroupManage.html', {'user_info': user_info})