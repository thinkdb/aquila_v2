from django.shortcuts import render, HttpResponse, redirect
from django.db.models import Q
from django.views import View
from back import forms
from dbms import models
from scripts import functions


class Login(View):
    def get(self, request):
        LoginForm = forms.LoginForm()
        return render(request, 'login.html', {'login_form': LoginForm})

    def post(self, request):
        LoginForm = forms.LoginForm(request.POST)
        ret = LoginForm.is_valid()

        if ret:
            username = request.POST.get("username", None)
            password = functions.py_password(request.POST.get("password", None))
            user_flag = models.UserInfo.objects.filter((Q(user_name=username) | Q(email=username)), user_pass=password).count()

            if user_flag:
                rem_flag = request.POST.get('Remember Me', None)
                sess = functions.OpSession()
                if rem_flag:
                    sess.login(request, username, 1)
                else:
                    sess.login(request, username)
                return redirect('index.html')
            else:
                return render(request, 'login.html', {'login_form': LoginForm,
                                                      "form_error": "用户名或者密码错误"})
        else:
            a = LoginForm.errors.as_json()

            return render(request, 'login.html', {'login_form': LoginForm})


class Register(View):
    def get(self, request):
        reg_form = forms.RegisterForm()
        return render(request, 'register.html', {'RegForm': reg_form})

    def post(self, request):
        reg_form = forms.RegisterForm(request.POST)
        ret = reg_form.is_valid()
        if ret:
            return render(request, 'register.html', {'RegForm': reg_form})
        else:
            return render(request, 'register.html', {'RegForm': reg_form})