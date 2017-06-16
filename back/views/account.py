from django.shortcuts import render, redirect
from django.db.models import Q
from django.views import View
from back import forms
from model_model import models
from scripts import functions


class Login(View):
    def get(self, request):
        LoginForm = forms.LoginForm()
        return render(request, 'login.html', {'login_form': LoginForm})

    def post(self, request):
        LoginForm = forms.LoginForm(request.POST)
        if LoginForm.is_valid():
            username = request.POST.get("username", None)
            password = functions.py_password(request.POST.get("password", None))
            user_info = models.UserInfo.objects.filter((Q(user_name=username) |
                                                        Q(email=username)), user_pass=password).all()
            if user_info:
                rem_flag = request.POST.get('Remember Me', None)
                sess = functions.OpSession()
                if rem_flag:
                    sess.login(request, username, 1)
                else:
                    sess.login(request, username)
                return redirect('/index.html')
            else:
                return render(request, 'login.html', {'login_form': LoginForm,
                                                      "form_error": "用户名或者密码错误"})
        else:
            return render(request, 'login.html', {'login_form': LoginForm})


class Register(View):
    def get(self, request):
        reg_form = forms.RegisterForm()
        return render(request, 'register.html', {'RegForm': reg_form})

    def post(self, request):
        reg_form = forms.RegisterForm(request.POST)
        ret = reg_form.is_valid()
        if ret:
            models.UserInfo.objects.create(
                user_name=request.POST['username'],
                user_pass=functions.py_password(request.POST['password']),
                email=request.POST['email'],
                lock_flag=0,
                role_id=2,
                user_group_id=2
            )
            return redirect('login.html')
        else:
            return render(request, 'register.html', {'RegForm': reg_form})