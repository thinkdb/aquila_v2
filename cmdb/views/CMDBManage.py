from django.shortcuts import render, HttpResponse
from django.views import View
from model_model import models
from cmdb import forms
from back.views.AuthAccount import AuthAccount, GetUserInfo
from django.utils.decorators import method_decorator
from scripts.functions import JsonCustomEncoder
import json


@method_decorator(AuthAccount, name='dispatch')
class HostManage(View):
    def get(self, request):
        user_info = GetUserInfo(request)
        host_info = models.HostInfo.objects.all()
        host_form = forms.HostAppend()
        return render(request, 'HostManage.html', {'user_info': user_info,
                                                   'host_info': host_info,
                                                   'host_form': host_form,
                                                   'request_path': request.path_info,
                                                   })

    def post(self, request):
        # delete
        hid_list = request.POST.get('host_list', None)
        gid_list = request.POST.get('group_list', None)
        if hid_list or gid_list:
            group_id_list = []
            host_id_list = []
            if len(hid_list):
                for item in hid_list.split(','):
                    host_id_list.append(int(item))
            if len(gid_list):
                for item in gid_list.split(','):
                    group_id_list.append(int(item))
            data = {'msg': '', 'flag': 1}
            try:
                if len(host_id_list):
                    r = models.HostInfo.objects.filter(id__in=host_id_list).delete()
                    data['msg'] = r
                if len(group_id_list):
                    r = models.HostGroup.objects.filter(id__in=group_id_list).delete()
                    data['msg'] = r
            except Exception as e:
                data['msg'] = e
                data['flag'] = 0
            return HttpResponse(json.dumps(data))

        obj = forms.HostAppend(request.POST)
        if obj.is_valid():
            host_id = request.POST.get('host_id', None)
            # add
            if not host_id:
                try:
                    r = models.HostInfo.objects.create(
                        host_ip=obj.cleaned_data['host_ip'],
                        app_type_id=obj.cleaned_data['app_type'],
                        host_group_id=obj.cleaned_data['host_group'],
                        host_pass=obj.cleaned_data['host_pass'],
                        host_port=obj.cleaned_data['host_port'],
                        host_user=obj.cleaned_data['host_user']
                    )
                    app_user = obj.cleaned_data['app_user']
                    app_pass = obj.cleaned_data['app_pass']
                    app_port = obj.cleaned_data['app_port']
                    if app_user or app_pass or app_port:
                        models.HostAPPAccount.objects.create(
                            app_user=app_user,
                            app_port=app_port,
                            app_pass=app_pass,
                            host=r
                        )
                    ret = {'flag': 1, 'data': 1}
                except Exception as e:
                    ret = {'flag': 0, 'data': e}
            else:
                models.HostInfo.objects.filter(id=obj.cleaned_data['host_id']).update(
                    host_ip=obj.cleaned_data['host_ip'],
                    app_type_id=obj.cleaned_data['app_type'],
                    host_group_id=obj.cleaned_data['host_group'],
                    host_pass=obj.cleaned_data['host_pass'],
                    host_port=obj.cleaned_data['host_port'],
                    host_user=obj.cleaned_data['host_user']
                )

                app_user = obj.cleaned_data['app_user']
                app_pass = obj.cleaned_data['app_pass']
                app_port = obj.cleaned_data['app_port']

                if app_user or app_pass or app_port:
                    r = models.HostInfo.objects.filter(id=obj.cleaned_data['host_id']).first()
                    app_flag = models.HostAPPAccount.objects.filter(host=r).count()
                    if app_flag:
                        models.HostAPPAccount.objects.filter(host=r).update(
                            app_user=app_user,
                            app_port=app_port,
                            app_pass=app_pass,
                        )
                    else:
                        models.HostAPPAccount.objects.create(
                            app_user=app_user,
                            app_port=app_port,
                            app_pass=app_pass,
                            host=r
                        )

                ret = {'flag': 2, 'data': 1}
        else:
            ret = {'flag': 0, 'data': obj.errors}
        return HttpResponse(json.dumps(ret, cls=JsonCustomEncoder))


@method_decorator(AuthAccount, name='dispatch')
class HostGroupManage(View):
    def get(self, request):
        user_info = GetUserInfo(request)
        return render(request, 'HostGroupManage.html', {'user_info': user_info})

    def post(self, request):
        pass


@method_decorator(AuthAccount, name='dispatch')
class UserManage(View):
    def get(self, request):
        user_info = GetUserInfo(request)
        return render(request, 'HostGroupManage.html', {'user_info': user_info})

    def post(self, request):
        pass


@method_decorator(AuthAccount, name='dispatch')
class UserGroupManage(View):
    def get(self, request):
        user_info = GetUserInfo(request)
        return render(request, 'HostGroupManage.html', {'user_info': user_info})

    def post(self, request):
        pass


@method_decorator(AuthAccount, name='dispatch')
class PrivManage(View):
    def get(self, request):
        user_info = GetUserInfo(request)
        return render(request, 'HostGroupManage.html', {'user_info': user_info})

    def post(self, request):
        pass


@method_decorator(AuthAccount, name='dispatch')
class PrivGroupManage(View):
    def get(self, request):
        user_info = GetUserInfo(request)
        return render(request, 'HostGroupManage.html', {'user_info': user_info})

    def post(self, request):
        pass