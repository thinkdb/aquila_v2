from django.shortcuts import render, HttpResponse
from django.views import View
from model_model import models
from back.views.AuthAccount import AuthAccount
from django.utils.decorators import method_decorator
from dbms.tasks import get_matedata


@method_decorator(AuthAccount, name='dispatch')
class GetMetaData(View):
    def get(self, request):
        host_info = models.HostInfo.objects.filter(app_type__app_name='MySQL').values('host_ip')
        db_info = models.MetaDataDatabase.objects.filter(host_ip='192.168.1.4').all()
        table_list = models.MetaDataTables.objects.filter(host_ip='192.168.1.4', table_schema='monitor').all()
        table_info = models.MetaDataTables.objects.filter(host_ip='192.168.1.4',
                                                          table_schema='monitor',
                                                          table_name='base_info').all()
        column_info = models.MetaDataColumns.objects.filter(host_ip='192.168.1.4',
                                                            table_schema='monitor',
                                                            table_name='base_info').all()
        index_info = models.MetaDataIndexs.objects.filter(host_ip='192.168.1.4',
                                                          table_schema='monitor',
                                                          table_name='base_info').all()
        table_sc = models.MetaDataTableStructure.objects.filter(table__host_ip='192.168.1.4').all()

        return render(request, 'get_metadata.html', {'host_info': host_info,
                                                     'db_info': db_info,
                                                     'table_list': table_list,
                                                     'table_info': table_info,
                                                     'column_info': column_info,
                                                     'index_info': index_info,
                                                     'table_sc': table_sc})

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


@method_decorator(AuthAccount, name='dispatch')
class CollectMetadata(View):
    def get(self, request):
        return render(request, 'collect_metadata.html')

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