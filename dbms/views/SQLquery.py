from django.shortcuts import render, HttpResponse
from django.views import View
from model_model import models
from dbms import forms
from back.views.AuthAccount import AuthAccount, GetUserInfo
from django.utils.decorators import method_decorator
from scripts import functions


@method_decorator(AuthAccount, name='dispatch')
class SqlCommit(View):
    def get(self, request):
        pass

    def post(self, request):
        pass