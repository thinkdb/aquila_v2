from django.forms import Form, widgets, fields
from django.forms.models import ValidationError
from django.db.models import Q
from scripts import functions
from model_model import models
import re


class LoginForm(Form):
    username = fields.CharField(error_messages={'required': '用户名不能为空'},
                                widget=widgets.TextInput(attrs={
                                    'class': 'form-control',
                                    'placeholder': 'Username'
                                }))
    password = fields.CharField(error_messages={'required': '密码不能为空'},
                                widget=widgets.PasswordInput(attrs={
                                    'class': 'form-control',
                                    'placeholder': 'Password'
                                }))

    # def clean(self):
    #     user_token = self.cleaned_data['username']
    #     pass_token = functions.py_password(self.cleaned_data['password'])
    #
    #     user_flag = models.UserInfo.objects.filter((Q(user_name=user_token) | Q(email=user_token)),
    #                                                user_pass=pass_token).count()
    #     if not user_flag:
    #         raise ValidationError(message='用户名或者密码错误', code='form_error')


class RegisterForm(Form):
    username = fields.CharField(error_messages={'required': '用户名不能为空',
                                                'max_length': '长度不能超过15个字符',
                                                'min_length': '长度不能小于5个字符'
                                                },
                                max_length=15,
                                min_length=5,
                                required=True,
                                widget=widgets.TextInput(attrs={
                                    'class': 'form-control',
                                    'placeholder': 'Username'
                                }),
                                validators=[]
                                )

    password = fields.CharField(error_messages={'required': '密码不能为空',
                                                'max_length': '长度不能超过16个字符',
                                                'min_length': '长度不能小于8个字符'
                                                },
                                max_length=16,
                                min_length=8,
                                required=True,
                                widget=widgets.PasswordInput(attrs={
                                    'class': 'form-control',
                                    'placeholder': 'Password'
                                }))

    email = fields.EmailField(error_messages={'required': '邮件不能为空'},
                              widget=widgets.PasswordInput(attrs={
                                  'class': 'form-control',
                                  'placeholder': 'Email',
                                  'type': 'email'
                              }))

    def clean_username(self):
        user_str = self.cleaned_data['username']
        result = re.search('^[a-zA-Z]*([a-zA-Z0-9]|[_]){5,15}$', user_str)
        user_flag = models.UserInfo.objects.filter(user_name=self.cleaned_data['username']).count()

        if not result:
            raise ValidationError(message='用户名只能以字母开头,由下划线、字母和数字组成\n'
                                          '长度为5到15个字符', code='username_error')
        if user_flag:
            raise ValidationError(message='用户已经存在', code='username_exists_error')

    def clean_password(self):
        password_str = self.cleaned_data['password']
        len_result = re.search('^(\w+){8,16}$', password_str)
        num_result = re.search('^[\d]*$', password_str)
        str_result = re.search('^[A-Za-z]*$', password_str)
        if len_result and not num_result and not str_result:
            pass
        else:
            raise ValidationError(message='密码由8到16个字符组成，必须由字母、数字、下划线组成', code='email_error')

    def clean_email(self):
        email_str = self.cleaned_data['email']
        result = re.search('^([a-zA-Z0-9]+[_|\_|\.]?)*[a-zA-Z0-9]+@([a-zA-Z0-9]+[_|\_|\.]?)*'
                           '[a-zA-Z0-9]+\.[a-zA-Z]{2,3}$', email_str)
        user_flag = models.UserInfo.objects.filter(email=self.cleaned_data['email']).count()

        if not result:
            raise ValidationError(message='邮箱格式错误或者内容不合法', code='email_error')

        if user_flag:
            raise ValidationError(message='邮箱已经存在', code='email_exists_error')
