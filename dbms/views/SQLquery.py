from django.shortcuts import render, HttpResponse
from django.views import View
from model_model import models
from dbms import forms
from back.views.AuthAccount import AuthAccount
from django.utils.decorators import method_decorator
from scripts import functions


@method_decorator(AuthAccount, name='dispatch')
class SqlQuery(View):
    def get(self, request):
        SqlQuerform = forms.SQLQueryForm()
        return render(request, 'sqlquery/sql_query.html', {'sql_from': SqlQuerform})

    def post(self, request):
        SqlQuerform = forms.SQLQueryForm(request.POST)
        host_ip = request.POST.get('host_ip', None)
        port = request.POST.get('host_port', None)
        schema_name = request.POST.get('schema_name', None)
        sql_content = request.POST.get('sql_content', None)
        if host_ip != '----' and port != '----' and schema_name != '----':
            host_info = models.HostAPPAccount.objects.filter(host__id=host_ip,
                                                             app_port=port).values_list('host__host_ip',
                                                                                        'app_user',
                                                                                        'app_pass')
        else:
            error_msg = '请选择相应的主机、端口和库名'
            return render(request, 'sqlquery/sql_query.html', {'sql_from': SqlQuerform,
                                                               'error_msg': error_msg})
        ip = host_info[0][0]
        user = host_info[0][1]
        app_pass = host_info[0][2]

        sql_api = functions.DBAPI(host=ip, user=user, port=port, password=app_pass, database=schema_name)
        if sql_api.error:
            return render(request, 'sqlquery/sql_query.html', {'sql_from': SqlQuerform,
                                                               'error_msg': sql_api.error})
        else:
            sql_result = sql_api.conn_query(sql_content)
            col_result = sql_api.get_col()
            return render(request, 'sqlquery/sql_query.html', {'sql_from': SqlQuerform,
                                                               'sql_result': sql_result,
                                                               'col_result': col_result})


class SqlDump(View):
    def post(self, request):
        pass