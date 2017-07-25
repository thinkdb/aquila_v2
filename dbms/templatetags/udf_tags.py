from django import template
register = template.Library()
from django.utils.safestring import mark_safe
from scripts import SQLparser


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
def build_slow_recodes(slow_obj, host_id):
    td_str = ""
    if slow_obj:
        for line in slow_obj:
            td_str += "<tr><td>{dbname}</td><td>{ts_cnt}</td>" \
                      "<td>{sum_query}</td><td>{max_query}</td><td>{min_query}</td>" \
                      "<td>{sum_lock}</td><td>{max_lock}</td><td>{min_lock}</td>" \
                      "<td><a class='show_sql'>显示完整语句</a></td><td>".format(dbname=line['slowqueryhistory__db_max'],
                                                                           ts_cnt=int(line['ts_cnt']),
                                                                           sum_query=line['sum_query_time'],
                                                                           min_query=line['min_query_time'],
                                                                           max_query=line['max_query_time'],
                                                                           sum_lock=line['sum_lock_time'],
                                                                           min_lock=line['min_lock_time'],
                                                                           max_lock=line['max_lock_time'])
            # 过滤无法获取执行计划的语句
            sql_content = SQLparser.QueryRewrite().format_sql(line['sample'])
            if sql_content:
                td_str += "<a id='{class_name}' href='/dbms/query_optimize-{host_id}-{sid}.html'>查看详情</a>" \
                          "</td></tr>".format(class_name=line['checksum'],
                                              sid=line['checksum'],
                                              host_id=host_id)
            else:
                td_str += "<span>查看详情</span></td></tr>"

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
    if abs(contacts.number - page_counter) <= 10:
        ele = '''<li><a href="?page=%s&slow_id=%s">%s</a></li>''' % (page_counter, host_id, page_counter)
    if contacts.number == page_counter:
        ele = '''<li class="active"><a href="?page=%s&slow_id=%s">%s</a></li>''' % (page_counter, host_id, page_counter)
    return mark_safe(ele)


@register.simple_tag
def render_page_previous_next(contacts, host_id):
    return "?page=%s&slow_id=%s" % (contacts, host_id)


@register.simple_tag
def build_optimize_recodes(slow_obj):
    td_str = ""
    if slow_obj:
        for line in slow_obj:
            td_str += "<tr><td>{dbname}</td><td>{ts_cnt}</td>" \
                      "<td>{first_seen}</td><td>{last_seen}</td>" \
                      "<td>{sum_query}</td><td>{max_query}</td><td>{min_query}</td>" \
                      "<td>{sum_lock}</td><td>{max_lock}</td><td>{min_lock}</td><td>优化</td>" \
                      "</tr>".format(dbname=line['slowqueryhistory__db_max'],
                                     ts_cnt=int(line['ts_cnt']),
                                     sum_query=line['sum_query_time'],
                                     min_query=line['min_query_time'],
                                     max_query=line['max_query_time'],
                                     sum_lock=line['sum_lock_time'],
                                     min_lock=line['min_lock_time'],
                                     first_seen=line['first_seen'],
                                     last_seen=line['last_seen'],
                                     max_lock=line['max_lock_time'])

    return mark_safe(td_str)


@register.simple_tag
def build_explain_info(explain_col, explain_result):
    """
    显示SQL语句的执行计划
    :param explain_col: 列名
    :param explain_result: 执行计划结果
    :return: 返回拼接好的表格
    """
    table_str = build_table(explain_col, explain_result)
    return mark_safe(table_str)


@register.simple_tag
def build_slow_query_rely_info(table_info_dict):
    """
    显示优化慢sql语句依赖信息，表、索引
    :param table_info_dict: 后台返回的表、索引 信息
    :return:
    """
    all_info_str = ""
    for table_name in table_info_dict.keys():
        div_str = "<div class='panel panel-default base_info' style='border-color: #2aabd2;margin-top: 10px;'>" \
                  "<div class='panel-heading show_query_rely' " \
                  "style='background-color: #2aabd2; color: white; '>查看{table}表详情</div>" \
                  "<div class='hidden' ><h4>状态信息</h4>" \
                   "<div style='overflow: scroll;'>{base_info}</div>" \
                   "<h4>索引信息</h4>" \
                   "{index_info}" \
                   "<h4>表结构信息</h4>" \
                   "{str_info}" \
                   "</div></div>"
        # 默认只显示表名， 点表名展开这张表的所有信息
        table_tbody = table_info_dict[table_name]['table_info']['status']
        table_thead = table_info_dict[table_name]['table_info']['col']
        table_base_info = build_table(table_thead, table_tbody)

        index_tbody = table_info_dict[table_name]['index_info']['status']
        index_thead = table_info_dict[table_name]['index_info']['col']
        table_index_info = build_table(index_thead, index_tbody)

        str_tbody = table_info_dict[table_name]['structure']['status']
        str_thead = table_info_dict[table_name]['structure']['col']
        structure_info = build_table(str_thead, str_tbody, type=1)

        div_str = div_str.format(table=table_name.lower(),
                                 base_info=table_base_info,
                                 index_info=table_index_info,
                                 str_info=structure_info)
        all_info_str += div_str

    return mark_safe(all_info_str)


def build_table(thead, tbody, type=None):
    table_str = "<table class='table table-bordered table-condensed'>" \
                "<thead><tr>{thead_str}</tr></thead>" \
                "<tbody>{tbody_str}</tbody>" \
                "</table>"
    thead_structure = ""
    tbody_structure = ""
    for col in thead:
        thead_structure += "<th>{col_name}</th>".format(col_name=col)

    if type:
        sql_str = ""
        for line in tbody:
            tbody_structure += "<tr>"
            for item in line[1].split('\n'):
                # 处理sql语句
                sql_str += "{sql_item}</br>".format(sql_item=item)
            tbody_structure += "<td>{col_1}</td><td>{item_name}</td></tr>".format(col_1=line[0],
                                                                                  item_name=sql_str)

    else:
        for line in tbody:
            tbody_structure += "<tr>"
            for item in line:
                tbody_structure += "<td>{item_name}</td>".format(item_name=item)
            tbody_structure += "</tr>"
    table_str = table_str.format(thead_str=thead_structure, tbody_str=tbody_structure)

    return table_str
