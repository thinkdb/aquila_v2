from django.shortcuts import render
from model_model import models


def test(request):
    field_list = []
    table_config = [
        {
            'q': 'id',
            'value': '',
            'display': 0
        },
        {
            'q': 'user_name',
            'value': '',
            'display': 1
        }
    ]
    for item in table_config:
        field_list.append(item['q'])

    uobj = models.UserInfo.objects.values(*field_list)
    for item in uobj:
        for col in field_list:
            for v in table_config:
                if v['q'] == col:
                    v['value'] = {col: item[col]}
    print(table_config)
    return render(request, 'test.html', {'table_head': table_config, 'table_body': uobj})