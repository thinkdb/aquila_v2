from django.shortcuts import render, HttpResponse
from django.views import View
from model_model import models
from back.views.AuthAccount import AuthAccount
from django.utils.decorators import method_decorator
from dbms.tasks import get_matedata


@method_decorator(AuthAccount, name='dispatch')
class GetMetaData(View):
    def get(self, request):
        return render(request, 'get_metadata.html')

    def post(self, request):
        account_list = models.HostAPPAccount.objects.values('host__host_ip',
                                                            'host__host_user',
                                                            'host__host_port',
                                                            'host__host_pass',
                                                            'app_port',
                                                            'app_pass',
                                                            'app_user'
                                                            )

        get_matedata(account_list)
        return HttpResponse('ok')