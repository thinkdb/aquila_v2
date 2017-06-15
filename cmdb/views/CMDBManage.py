from django.shortcuts import render
from django.views import View
from model_model import models
from cmdb import forms
from back.views.AuthAccount import AuthAccount, GetUserInfo


class HostManage(View):
    def get(self, request):
        user_info = GetUserInfo(request)
        host_info = models.HostInfo.objects.all()
        host_form = forms.HostAppend()
        return render(request, 'HostManage.html', {'user_info': user_info,
                                                   'host_info': host_info,
                                                   'host_form': host_form
                                                   })

    def post(self, request):
        pass


class HostGroupManage(View):
    def get(self, request):
        user_info = GetUserInfo(request)
        return render(request, 'HostGroupManage.html', {'user_info': user_info})

    def post(self, request):
        pass


class UserManage(View):
    def get(self, request):
        user_info = GetUserInfo(request)
        return render(request, 'HostGroupManage.html', {'user_info': user_info})

    def post(self, request):
        pass


class UserGroupManage(View):
    def get(self, request):
        user_info = GetUserInfo(request)
        return render(request, 'HostGroupManage.html', {'user_info': user_info})

    def post(self, request):
        pass


class PrivManage(View):
    def get(self, request):
        user_info = GetUserInfo(request)
        return render(request, 'HostGroupManage.html', {'user_info': user_info})

    def post(self, request):
        pass


class PrivGroupManage(View):
    def get(self, request):
        user_info = GetUserInfo(request)
        return render(request, 'HostGroupManage.html', {'user_info': user_info})

    def post(self, request):
        pass