from django.shortcuts import render, HttpResponse
from django.db.models import Count, Min, Max, Sum
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
        #     print(type(host[1]), host[1], host[0])
        slow_obj = None
        host_id = request.GET.get('slow_id', None)
        if host_id:
            host_id = int(host_id)
            host_obj = models.HostAPPAccount.objects.all().values_list('host__host_ip', 'id')
            slow_host_obj = models.HostAPPAccount.objects.filter(id=host_id).all()
            host_ip = slow_host_obj[0].host.host_ip
            app_user = slow_host_obj[0].app_user
            app_pass = slow_host_obj[0].app_pass
            app_port = slow_host_obj[0].app_port
            slow_obj = models.SlowQuery.objects.filter(
                reviewed_status__isnull=True,
                slowqueryhistory__hostname_max=host_ip
            ).values_list('fingerprint',
                          'first_seen',
                          'last_seen',
                          'slowqueryhistory__db_max',
                          'slowqueryhistory__hostname_max').annotate(c=Sum('slowqueryhistory__ts_cnt'))

        return render(request, 'SlowQuery/SlowQuery.html',
                      {
                          'slow_obj': slow_obj,
                          'host_obj': host_obj,
                          'host_id': host_id
                      })

    def post(self, request):
        host_id = request.POST.get('slow_id')
        # 根据上传的host_id 去获取对应的主机信息, 用于获取慢sql相关表信息
        host_obj = models.HostAPPAccount.objects.all().values_list('host__host_ip', 'id')
        slow_host_obj = models.HostAPPAccount.objects.filter(id=host_id).all()
        host_ip = slow_host_obj[0].host.host_ip
        app_user = slow_host_obj[0].app_user
        app_pass = slow_host_obj[0].app_pass
        app_port = slow_host_obj[0].app_port

        slow_obj = models.SlowQuery.objects.filter(
            reviewed_status__isnull=True
        ).values_list('fingerprint',
                      'first_seen',
                      'last_seen',
                      'slowqueryhistory__db_max',
                      'slowqueryhistory__hostname_max').annotate(c=Sum('slowqueryhistory__ts_cnt'))
        return render(request, 'SlowQuery/SlowQuery.html',
                      {
                        'slow_obj': slow_obj,
                        'host_obj': host_obj,
                        'host_id': host_id
                      })
