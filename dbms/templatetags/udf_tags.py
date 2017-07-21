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
    if slow_obj:
        for line in slow_obj:
            td_str += "<tr><td>{dbname}</td><td>{ts_cnt}</td>" \
                      "<td>{sum_query}</td><td>{max_query}</td><td>{min_query}</td>" \
                      "<td>{sum_lock}</td><td>{max_lock}</td><td>{min_lock}</td>" \
                      "<td><a class='show_sql'>显示完整语句</a></td><td><a id='{class_name}' href='#'>优化</a></td>" \
                      "</tr>".format(
                                     dbname=line['slowqueryhistory__db_max'],
                                     ts_cnt=int(line['ts_cnt']),
                                     sum_query=line['sum_query_time'],
                                     min_query=line['min_query_time'],
                                     max_query=line['max_query_time'],
                                     sum_lock=line['sum_lock_time'],
                                     min_lock=line['min_lock_time'],
                                     max_lock=line['max_lock_time'],
                                     class_name=line['checksum'])

            td_str += "<tr class='hidden {class_name}'><td colspan=11    class='show_sql'>" \
                      "<div><code><span>{span_str}</span></code></div>" \
                      "</td><td></tr>".format(span_str=line['sample'],
                                          class_name=line['checksum'])

    return mark_safe(td_str)


@register.simple_tag
def render_page_ele(page_counter, contacts, host_id):
    """
    :param page_counter: 循环的次数
    :param contacts: 分页的对象信息
    :return:
    """
    ele = ''
    filters = ''
    if abs(contacts.number - page_counter) <= 10:
        ele = '''<li><a href="?page=%s&slow_id=%s">%s</a></li>''' % (page_counter, host_id, page_counter)
    if contacts.number == page_counter:
        ele = '''<li class="active"><a href="?page=%s">%s</a></li>''' % (page_counter, page_counter)
    return mark_safe(ele)


@register.simple_tag
def render_page_previous_next(contacts, host_id):
    return "?page=%s&slow_id=%s" % (contacts, host_id)
