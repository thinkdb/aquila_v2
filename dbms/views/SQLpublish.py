from django.shortcuts import render, HttpResponse
from django.views import View
from model_model import models
from dbms import forms
from back.views.AuthAccount import AuthAccount, GetUserInfo
from django.utils.decorators import method_decorator
from scripts.functions import JsonCustomEncoder, tran_audit_result
from scripts.Inception import Inception
import json


@method_decorator(AuthAccount, name='dispatch')
class SqlCommit(View):
    def get(self, request):
        user_info = GetUserInfo(request)
        obj = forms.SqlComForm()

        return render(request,
                      'inception/SqlCommit.html',
                      {'user_info': user_info,
                       'SqlComFormObj': obj,

                       })

    def post(self, request):
        user_info = GetUserInfo(request)
        obj = forms.SqlComForm(request.POST)
        result_dict = {'data': {}, 'status': 0, 'error': '', 'running': 0}
        if obj.is_valid():
            result_dict['status'] = 1
            host_id = obj.cleaned_data['host']
            port = obj.cleaned_data['port']
            db_name = obj.cleaned_data['db_name']
            sql_content = 'use ' + db_name + ';' + obj.cleaned_data['sql_content']
            db_info = models.HostAPPAccount.objects.filter(host_id=host_id,
                                                           host__app_type__app_name='MySQL',
                                                           app_port=port
                                                           ).values('host__host_ip',
                                                                    'app_user',
                                                                    'app_pass')
            if obj.cleaned_data['is_commit'] == '1':
                # run sql
                result_dict['running'] = 1
                pass
            else:
                # audit sql
                ince = Inception(db_host=db_info[0]['host__host_ip'],
                                 db_user=db_info[0]['app_user'],
                                 db_passwd=db_info[0]['app_pass'],
                                 sql_content=sql_content)
                result = ince.audit_sql()
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
                        msg = '执行成功备份成功'
                    elif row[3] == 'Execute Successfully\nBackup filed':
                        msg = '执行成功备份失败'
                    else:
                        msg = '未知状态'

                    a = ''
                    for kxxxx, rows in enumerate(row[4].split('\n')):
                        a = a + rows + '---'
                    result_dict['data'][id]['status'] = msg
                    result_dict['data'][id]['error_msg'] = a
                    result_dict['data'][id]['sql'] = row[5]
                    result_dict['data'][id]['rows'] = row[6]

        else:
            result_dict['error'] = json.dumps(obj.errors)

        return render(request,
                      'inception/SqlCommit.html',
                      {'user_info': user_info,
                       'SqlComFormObj': obj,
                       'AuditResult': result_dict,
                       })


@method_decorator(AuthAccount, name='dispatch')
class SqlAudit(View):
    def get(self, request):
        user_info = GetUserInfo(request)
        return render(request, 'HostGroupManage.html', {'user_info': user_info})

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