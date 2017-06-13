from django.forms import Form, widgets, fields

class LoginForm(Form):
    username = fields.CharField(error_messages={'required': '用户名不能为空'},
                                widget=widgets.TextInput(attrs={
                                    'class': 'form-control',
                                    'placeholder': 'Username'
                                }),
                                label='用户名')
    password = fields.CharField(error_messages={'required': '密码不能为空'},
                                widget=widgets.PasswordInput(attrs={
                                    'class': 'form-control',
                                    'placeholder': 'Password'
                                }),
                                label='密    码')