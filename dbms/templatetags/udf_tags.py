from django import template
register = template.Library()
from django.utils.safestring import mark_safe


@register.simple_tag
def build_select_option(host_obj, host_id):
    option_str = ""
    for line in host_obj:
        if host_id:
            if line[1] == host_id:
                option_str += "<option selected value={host_id}>{host_ip}</option>".format(host_id=line[1],
                                                                                           host_ip=line[0])
            else:
                option_str += "<option value={host_id}>{host_ip}</option>".format(host_id=line[1],
                                                                                  host_ip=line[0])
        else:
            option_str += "<option value={host_id}>{host_ip}</option>".format(host_id=line[1],
                                                                              host_ip=line[0])
    return mark_safe(option_str)


@register.simple_tag
def build_slow_recodes(slow_obj):
    td_str = ""
    for line in slow_obj:
        if len(line[0]) >= 100:
            sql_str = "{col}</td><td><a>显示完整语句</a>".format(col=line[0][:100])
        else:
            sql_str = "{col}</td><td>".format(col=line[0])
        td_str += "<tr><td>{col1}</td><td>{col2}</td><td>{col3}</td>" \
                  "<td>{col4}</td><td>{col5}</td><td>{col6}</td></tr>".format(col1=line[4],
                                                                              col2=line[3],
                                                                              col3=line[1],
                                                                              col4=line[2],
                                                                              col5=int(line[5]),
                                                                              col6=sql_str)
    return mark_safe(td_str)