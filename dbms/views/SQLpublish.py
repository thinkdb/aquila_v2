from django.shortcuts import render, HttpResponse
from django.views import View
from model_model import models
from dbms import forms
from back.views.AuthAccount import AuthAccount, GetUserInfo
from django.utils.decorators import method_decorator
from scripts.functions import JsonCustomEncoder
import json


@method_decorator(AuthAccount, name='dispatch')
class SqlCommit(View):
    def get(self, request):
        user_info = GetUserInfo(request)
        return render(request, 'HostGroupManage.html', {'user_info': user_info})

    def post(self, request):
        user_info = GetUserInfo(request)
        return render(request, 'HostGroupManage.html', {'user_info': user_info})


@method_decorator(AuthAccount, name='dispatch')
class SqlAudit(View):
    def get(self, request):
        user_info = GetUserInfo(request)
        return render(request, 'HostGroupManage.html', {'user_info': user_info})

    def post(self, request):
        user_info = GetUserInfo(request)
        return render(request, 'HostGroupManage.html', {'user_info': user_info})


@method_decorator(AuthAccount, name='dispatch')
class SqlRunning(View):
    def get(self, request):
        user_info = GetUserInfo(request)
        return render(request, 'HostGroupManage.html', {'user_info': user_info})

    def post(self, request):
        pass


@method_decorator(AuthAccount, name='dispatch')
class SqlView(View):
    def get(self, request):
        user_info = GetUserInfo(request)
        return render(request, 'HostGroupManage.html', {'user_info': user_info})

    def post(self, request):
        user_info = GetUserInfo(request)
        return render(request, 'HostGroupManage.html', {'user_info': user_info})


@method_decorator(AuthAccount, name='dispatch')
class SqlDetail(View):
    def get(self, request, wid):
        user_info = GetUserInfo(request)
        return render(request, 'HostGroupManage.html', {'user_info': user_info})

    def post(self, request, wid):
        user_info = GetUserInfo(request)
        return render(request, 'HostGroupManage.html', {'user_info': user_info})