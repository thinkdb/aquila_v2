from django.forms import Form, fields, widgets
from model_model import models


class SqlComForm(Form):

    title = fields.CharField(
        max_length=60,
        label='工单标题',
        error_messages={'required': '标题不能为空'},
        widget=widgets.TextInput(attrs={'class': 'form-control',
                                        'style': 'min-width:200px; max-width:500px',
                                        'placeholder': '简述工单功能与作用'})
    )
    # version = fields.ChoiceField(
    #     label='发布版本号',
    #     widget=widgets.Select(choices=[],
    #                           attrs={'class': 'form-control',
    #                                  'style': 'min-width:200px; max-width:500px'})
    # )
    host = fields.CharField(
        label='数据库地址',
        widget=widgets.Select(choices=[],
                              attrs={'class': 'form-control',
                                     'id': 'chose_db_ip',
                                     'style': 'min-width:200px;'
                                              ' max-width:500px'
                                              ''})
    )
    port = fields.IntegerField(
        widget=widgets.NumberInput(attrs={'class': 'form-control',
                                          'style': 'min-width:200px; max-width:500px'}),
        label='端口',
        max_value=65530,
        min_value=1025,
        error_messages={'invalid': '请输入有效端口号',
                        'min_value': '请输入一个大于或等于1025的端口号',
                        'max_value': '请输入一个小于或等于65530的端口号'}
    )
    db_name = fields.CharField(
        label='库名',
        strip=True,
        widget=widgets.TextInput(attrs={'class': 'form-control',
                                        'style': 'min-width:200px; max-width:500px'})
    )
    review_name = fields.CharField(
        label='审核人',
        widget=widgets.Select(choices=[],
                              attrs={'class': 'form-control',
                                     'style': 'min-width:200px; max-width:500px'})
    )
    run_time = fields.DateTimeField(
        label='工单执行时间',
        required=False,

        widget=widgets.DateTimeInput(
            attrs={'class': 'form-control',
                   'style': 'min-width:200px; max-width:500px',
                   'placeholder': '时间格式为：2017-06-01 20:00:00 默认为立即执行'}
        )


    )
    is_commit = fields.ChoiceField(
        label='提交审核',
        initial=0,
        choices=((0, '否'), (1, '是')),
        widget=widgets.Select(attrs={'class': 'form-control',
                                     'style': 'min-width:200px; max-width:500px'}),
    )
    sql_content = fields.CharField(
        label='SQL 内容',
        error_messages={'required': 'SQL 内容不能为空'},
        widget=widgets.Textarea(attrs={'class': 'form-control',
                                       'style': 'min-width:200px;'
                                                'max-width:800px'})
    )

    def __init__(self, *args, **kwargs):
        super(SqlComForm, self).__init__(*args, **kwargs)
        # self.fields['version'].widget.choices = models.HostGroup.objects.values_list('id', 'host_group_jd')
        self.fields['host'].widget.choices = models.HostInfo.objects.values_list('id', 'host_ip')
        user_info = models.UserInfo.objects.filter(userrolerelationship__role_id=1).values_list('id', 'user_name')
        self.fields['review_name'].widget.choices = user_info

