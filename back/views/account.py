from django.shortcuts import render, HttpResponse
from django.views import View
from back import forms


class Login(View):
    global LoginForm
    LoginForm = forms.LoginForm()

    def get(self, request):
        return render(request, 'login.html', {'login_form': LoginForm})

    def post(self, requset):
        return render(requset, 'login.html', {'login_form': LoginForm})