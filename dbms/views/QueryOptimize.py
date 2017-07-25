from django.shortcuts import render, HttpResponse
from django.db.models import Count, Min, Max, Sum
from django.views import View
from model_model import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.conf import settings
from back.views.AuthAccount import AuthAccount, GetUserInfo
from django.utils.decorators import method_decorator
from scripts import functions, SQLparser, GetTableInfo


@method_decorator(AuthAccount, name='dispatch')
class QueryOptimize(View):
    def get(self, request, sid, host_id):
        user_info = GetUserInfo(request)
        slow_obj = models.SlowQuery.objects.filter(
            reviewed_status__isnull=True,
            checksum=sid
        ).values('sample',
                 'first_seen',
                 'last_seen',
                 'slowqueryhistory__db_max',
                 'slowqueryhistory__hostname_max'
                 ).annotate(ts_cnt=Sum('slowqueryhistory__ts_cnt'),
                            sum_query_time=Sum('slowqueryhistory__query_time_sum'),
                            min_query_time=Max('slowqueryhistory__query_time_min'),
                            max_query_time=Max('slowqueryhistory__query_time_max'),
                            sum_lock_time=Sum('slowqueryhistory__lock_time_sum'),
                            min_lock_time=Max('slowqueryhistory__lock_time_min'),
                            max_lock_time=Max('slowqueryhistory__lock_time_max')).order_by('-ts_cnt')
        db_name = slow_obj[0]['slowqueryhistory__db_max']
        slow_host_obj = models.HostAPPAccount.objects.filter(id=host_id).all()
        host_ip = slow_host_obj[0].host.host_ip
        app_user = slow_host_obj[0].app_user
        app_pass = slow_host_obj[0].app_pass
        app_port = slow_host_obj[0].app_port

        slow_db = functions.DBAPI(host=host_ip, user=app_user, password=app_pass,
                                  port=int(app_port), database=db_name)

        if slow_db.error:
            error_msg = '无法连接主机: {hostname}上的数据库, 错误信息: {error_msg}'.format(hostname=host_ip,
                                                                            error_msg=slow_db.error)
            return render(request, 'SlowQuery/QueryOptimize.html', {
                'slow_obj': slow_obj,
                'user_info': user_info,
                'error_msg': error_msg
            })
        else:
            sql_content = SQLparser.QueryRewrite().format_sql(slow_obj[0]["sample"])
            explain_sql = "explain " + sql_content.lower()
            explain_result = slow_db.conn_query(explain_sql)
            explain_col = slow_db.get_col()
            table_list = SQLparser.QueryTableParser().parse(explain_sql)
            table_info_dict = None
            if table_list:
                table_info_dict = GetTableInfo.get_table_info(slow_db, table_list)
            return render(request, 'SlowQuery/QueryOptimize.html', {
                'slow_obj': slow_obj,
                'user_info': user_info,
                'explain_result': explain_result,
                'explain_col': explain_col,
                'table_info_dict': table_info_dict
            })

    def post(self, request):
        pass