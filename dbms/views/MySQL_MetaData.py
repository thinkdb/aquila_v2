from django.shortcuts import render, HttpResponse
from django.views import View
from model_model import models
from back.views.AuthAccount import AuthAccount
from django.utils.decorators import method_decorator
from dbms.tasks import get_matedata
import json


@method_decorator(AuthAccount, name='dispatch')
class GetMetaData(View):
    def get(self, request):
        host_ip = request.GET.get('host_ip', None)
        host_ip = '127.0.0.1'
        table_schema = 'monitor'
        table_name = 'base_info'
        host_info = models.HostInfo.objects.filter(app_type__app_name='MySQL').values('host_ip')
        db_info = models.MetaDataDatabase.objects.filter(host_ip=host_ip).all()
        table_list = models.MetaDataTables.objects.filter(host_ip=host_ip, table_schema=table_schema).all()
        # table_info = models.MetaDataTables.objects.filter(host_ip=host_ip,
        #                                                   table_schema=table_schema,
        #                                                   table_name=table_name).all()
        # column_info = models.MetaDataColumns.objects.filter(host_ip=host_ip,
        #                                                     table_schema=table_schema,
        #                                                     table_name=table_name).all()
        # index_info = models.MetaDataIndexs.objects.filter(host_ip=host_ip,
        #                                                   table_schema=table_schema,
        #                                                   table_name=table_name).all()
        # table_sc = models.MetaDataTableStructure.objects.filter(table__host_ip=host_ip).all()

        return render(request, 'get_metadata.html', {'host_info': host_info,
                                                     'db_info': db_info,
                                                     'table_list': table_list,
                                                     # 'table_info': table_info,
                                                     # 'column_info': column_info,
                                                     # 'index_info': index_info,
                                                     # 'table_sc': table_sc
                                                     })

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


@method_decorator(AuthAccount, name='dispatch')
class GetTableInfo(View):
    def get(self, request):
        result_dict = {'table_info': {},
                       'column_info': {},
                       'index_info': {},
                       'table_sc': {'sql_content': ''}
                       }
        host_ip = request.GET.get('host_ip', None)
        table_schema = request.GET.get('table_schema', None)
        table_name = request.GET.get('table_name', None)
        table_info = models.MetaDataTables.objects.filter(host_ip=host_ip,
                                                          table_schema=table_schema,
                                                          table_name=table_name).all()
        column_info = models.MetaDataColumns.objects.filter(host_ip=host_ip,
                                                            table_schema=table_schema,
                                                            table_name=table_name).all()
        index_info = models.MetaDataIndexs.objects.filter(host_ip=host_ip,
                                                          table_schema=table_schema,
                                                          table_name=table_name).all()
        table_sc = models.MetaDataTableStructure.objects.filter(table__host_ip=host_ip).all()
        for item in table_info:
            result_dict['table_info']['table_name'] = item.table_name
            result_dict['table_info']['engine'] = item.engine
            result_dict['table_info']['row_format'] = item.row_format
            result_dict['table_info']['table_rows'] = item.table_rows
            result_dict['table_info']['avg_row_length'] = item.avg_row_length
            result_dict['table_info']['max_data_length'] = item.max_data_length
            result_dict['table_info']['data_length'] = item.data_length
            result_dict['table_info']['index_length'] = item.index_length
            result_dict['table_info']['data_free'] = item.data_free
            result_dict['table_info']['chip_size'] = item.chip_size
            result_dict['table_info']['auto_increment'] = item.auto_increment
            result_dict['table_info']['table_collation'] = item.table_collation
            # result_dict['table_info']['create_time'] = item.create_time
            # result_dict['table_info']['create_time'] = item.create_time
            # result_dict['table_info']['check_time'] = item.check_time
            result_dict['table_info']['table_comment'] = item.table_comment
        print(result_dict)
        return HttpResponse(json.dumps(result_dict))