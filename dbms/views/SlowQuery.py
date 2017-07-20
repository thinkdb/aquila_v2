from django.shortcuts import render, HttpResponse
from django.views import View
from model_model import models
from django.conf import settings
from back.views.AuthAccount import AuthAccount
from django.utils.decorators import method_decorator
from scripts import functions


@method_decorator(AuthAccount, name='dispatch')
class SlowQuery(View):
    def get(self, request):
        host_obj = models.HostAPPAccount.objects.all().values_list('host__host_ip', 'id')
        # for host in host_obj:
        #     print(host[0], host[1])
        return render(request, 'SlowQuery/SlowQuery.html',
                      {'host_obj': host_obj})

    def post(self, request):
        print(request.POST)
        host_id = request.POST.get('slow_id')
        host_obj = models.HostAPPAccount.objects.filter(id=host_id).all()

        host_ip = host_obj[0].host.host_ip

        # 去 aquila 库根据这个ip 去查慢日志信息

        host = settings.DATABASES['default']['HOST']
        user = settings.DATABASES['default']['USER']
        password = settings.DATABASES['default']['PASSWORD']
        port = settings.DATABASES['default']['PORT']
        db_name = settings.DATABASES['default']['NAME']

        db_conn = functions.DBAPI(host=host, user=user, port=port, password=password)

        sql = """查询慢日志表"""
        db_conn.conn_query(sql)