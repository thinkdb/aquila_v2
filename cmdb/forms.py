from django.forms import Form, widgets, fields
from django.forms.models import ValidationError
from model_model import models


class HostAppend(Form):
    host_id = fields.CharField(widget=widgets.TextInput(attrs={'style': 'display: none;'}),
                               required=False,
                               label=id)
    host_ip = fields.GenericIPAddressField(error_messages={'required': '主机地址不能为空',
                                                           'invalid': 'IP地址不合法'},
                                           protocol='ipv4',
                                           label='主机地址',
                                           widget=widgets.TextInput(attrs={'class': 'form-control'}),
                                           strip=True
                                           )
    host_user = fields.CharField(label='主机用户',
                                 widget=widgets.TextInput(attrs={'class': 'form-control'}),
                                 strip=True)
    host_pass = fields.CharField(label='主机密码',
                                 widget=widgets.TextInput(attrs={'class': 'form-control'}),
                                 strip=True)
    host_port = fields.CharField(label='主机端口',
                                 initial=22,
                                 widget=widgets.TextInput(attrs={'class': 'form-control'}),
                                 error_messages={'required': 'host_port: 请输入有效端口号'},
                                 strip=True)

    app_type = fields.CharField(
        widget=widgets.Select(choices=[]),
        label='应用类型',
        error_messages={'required': '应用类型不能为空'},
        strip=True
    )
    host_group = fields.CharField(
        widget=widgets.Select(choices=[]),
        label='主机组',
        error_messages={'required': '主机组不能为空'},
        strip=True
    )
    app_user = fields.CharField(required=False,
                                label='应用用户',
                                widget=widgets.TextInput(attrs={'class': 'form-control'}),
                                strip=True)
    app_pass = fields.CharField(required=False,
                                label='应用密码',
                                widget=widgets.TextInput(attrs={'class': 'form-control'}),
                                strip=True)
    app_port = fields.CharField(required=False,
                                label='应用端口',
                                widget=widgets.TextInput(attrs={'class': 'form-control'}),
                                error_messages={'required': 'app_port: 请输入有效端口号'},
                                strip=True)

    def __init__(self, *args, **kwargs):
        super(HostAppend, self).__init__(*args, **kwargs)
        self.fields['host_group'].widget.choices = models.HostGroup.objects.values_list('id', 'host_group_jd')
        self.fields['app_type'].widget.choices = models.AppType.objects.values_list('id', 'app_name')

    # def clean_host_ip(self):
    #     ip = self.cleaned_data['host_ip']
    #     host_ip = models.HostInfo.objects.filter(host_ip=ip).count()
    #     if host_ip:
    #         raise ValidationError(message='%s: 主机已经存在' % ip, code='host_exists_error')
