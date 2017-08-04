from django.shortcuts import render, HttpResponse
from django.db.models import Count, Min, Max, Sum
from django.views import View
from model_model import models
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from back.views.AuthAccount import AuthAccount, GetUserInfo
from django.utils.decorators import method_decorator


@method_decorator(AuthAccount, name='dispatch')
class SlowQuery(View):
    def get(self, request):
        user_info = GetUserInfo(request)
        host_obj = models.HostAPPAccount.objects.all().values_list('host__host_ip', 'id')
        slow_obj = None
        host_id = request.GET.get('slow_id', None)
        page_numbers = 10
        contacts = ""
        if host_id:
            host_id = int(host_id)
            host_obj = models.HostAPPAccount.objects.all().values_list('host__host_ip', 'id')
            slow_host_obj = models.HostAPPAccount.objects.filter(id=host_id).all()
            host_ip = slow_host_obj[0].host.host_ip

            slow_obj = models.SlowQuery.objects.filter(
                reviewed_status__isnull=True,
                slowqueryhistory__hostname_max=host_ip
            ).values('aid',
                     'checksum',
                     'sample',
                     'slowqueryhistory__db_max',
                     'slowqueryhistory__hostname_max'
                     ).annotate(ts_cnt=Sum('slowqueryhistory__ts_cnt'),
                                sum_query_time=Sum('slowqueryhistory__query_time_sum'),
                                min_query_time=Max('slowqueryhistory__query_time_min'),
                                max_query_time=Max('slowqueryhistory__query_time_max'),
                                sum_lock_time=Sum('slowqueryhistory__lock_time_sum'),
                                min_lock_time=Max('slowqueryhistory__lock_time_min'),
                                max_lock_time=Max('slowqueryhistory__lock_time_max')).order_by('-ts_cnt')
        if slow_obj:
            paginator = Paginator(slow_obj, page_numbers)
            page = request.GET.get('page')
            try:
                contacts = paginator.page(page)
            except PageNotAnInteger:
                # If page is not an integer, deliver first page.
                contacts = paginator.page(1)
            except EmptyPage:
                # If page is out of range (e.g. 9999), deliver last page of results.
                contacts = paginator.page(paginator.num_pages)

        return render(request, 'SlowQuery/SlowQuery.html',
                      {
                          'slow_obj': slow_obj,
                          'host_obj': host_obj,
                          'host_id': host_id,
                          'contacts': contacts,
                          'user_info': user_info
                      })

    def post(self, request):
        slow_obj = host_id = None
        host_obj = models.HostAPPAccount.objects.all().values_list('host__host_ip', 'id')
        return render(request, 'SlowQuery/SlowQuery.html',
                      {'slow_obj': slow_obj,
                       'host_obj': host_obj,
                       'host_id': host_id})
