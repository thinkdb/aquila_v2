/**
 * Created by Administrator on 2017/4/26.
 */
/* 转换数字为ip地址 */
// $(function () {
//     $('td[id="num_to_ip"]').each(function () {
//         var num_ip = $(this).text();
//         if(num_ip < 0 || num_ip > 0xFFFFFFFF){
//             throw ("The number is not normal!");
//         }
//         var new_ip = (num_ip>>>24) + "." + (num_ip>>16 & 0xFF) + "." + (num_ip>>8 & 0xFF) + "." + (num_ip & 0xFF);
//         $(this).text(new_ip);
//     });
//
// });

$(function(){
    $.ajaxSetup({
            beforeSend:function (xhr, settings) {
                xhr.setRequestHeader('X-CSRFtoken', $.cookie('csrftoken'));
            }
        });

    $('#host_group_append').click(function () {
        $('.shade_layer').removeClass('check_dis_flag');
    });

    $('tbody').delegate("button", "click", function () {
        // 获取主机组的id
        var group_name = $(this).parent().parent().find('#group_name').text();
        var group_jd = $(this).parent().parent().find('#group_jd').text();
        var group_id = $(this).parent().parent().find('#hostgroup_id').text();

        // 获取主机的信息
        var host_id = $(this).parent().parent().find('#host_id').text();
        var num_to_ip = $(this).parent().parent().find('#num_to_ip').text();
        var app_type = $(this).parent().parent().find('#app_type').text();
        var host_group_id = $(this).parent().parent().find('#host_group_id').text();
        var host_user = $(this).parent().parent().find('#host_user').text();
        var host_pass = $(this).parent().parent().find('#host_pass').text();
        var host_port = $(this).parent().parent().find('#host_port').text();

        $('.shade_layer').removeClass('check_dis_flag');
        // 填充数据
        $('#groupname').val(group_name);
        $('#groupdesc').val(group_jd);
        $('#groupid').text(group_id);

        $('#id_host_id').val(host_id);
        $('#id_host_ip').val(num_to_ip);
        $('#id_app_type').val(app_type);
        $('#id_host_group').val(host_group_id);
        $('#id_host_user').val(host_user);
        $('#id_host_pass').val(host_pass);
        $('#id_host_port').val(host_port);



        // alert(a);
    });

    $('tbody #workruning_smt').click(function () {
        // 执行工单内容
        alert('正在执行中, 请备重复执行!!!!!!')
            $.ajax({
                url: '/dbms/inception/work_runing.html',
                type: 'POST',
                data: {'wid':$(this).parent().parent().find('#wid').text(),
                    'host_ip': $(this).parent().parent().find('#host_ip').text(),
                    'sql_content': $(this).parent().parent().find('#sql_content').text()},
                dataType: 'json',
                headers: {'X-CSRFtoken': $.cookie('csrftoken')},
                success: function (data) {
                    if(data==1){
                        alert('已经执行结束, 请移步到《工单查询》中查看执行结果!!!!!!');
                    }
                },
                error: function (data) {
                    console.log(data);
                }
            })

    });

    $('#dataTables-example').DataTable({
        responsive: true
    });
});

$('#group_add_button').click(function () {
    $.ajax({
        url: '/backend/hostgroup_append.html',
        type: 'POST',
        data: {'groupname': $('#groupname').val(), 'groupdesc': $('#groupdesc').val(), 'groupid':$('#groupid').text()},
        dataType: 'json',
        headers: {'X-CSRFtoken': $.cookie('csrftoken')},
        success: function (data) {
            flag = data.flag;
            msg_msg = data.msg;
            if (flag)
                location.reload();
            else
                $('#groupadd_err_msg').text(msg_msg);
        }
    })
});

$('#host_update').click(function () {
    $.ajax({
        url: '/cmdb/host/manage.html',
        type: 'POST',
        data: $('#form').serialize(),
        dataType: 'json',
        headers: {'X-CSRFtoken': $.cookie('csrftoken')},
        success: function (data) {
            flag = data.flag;
            msg_msg = data.msg;
            if (flag)
                location.reload();
            else
                $('#err_msg').text(msg_msg);
        }
    })
});

$('#exit_edit').click(function () {
    $('.shade_layer').addClass('check_dis_flag');
});


$('#host_append').click(function(){
    $.ajax({
        url: '/cmdb/host/manage.html',
        type: 'POST',
        data: $('#form').serialize(),
        dataType: 'json',
        headers: {'X-CSRFtoken': $.cookie('csrftoken')},
        success: function (data) {
            flag = data.flag;
            msg_msg = data.data;
            if (flag)
                location.reload();
            else
                $.each(msg_msg, function(key, value){
                    $('#err_msg').text(value);
                });

        }
    })
});


$('#host_delete').click(function(){
    var host_list = new Array();
    var group_list = new Array();
    $('#host input[type="checkbox"]').each(function () {
        if($(this).prop('checked')){
            var host = $(this).parent().parent().find('#host_id').text();
            host_list.push(host);
        }
    });
    $('#hostgroup input[type="checkbox"]').each(function () {
        if($(this).prop('checked')){
            var group = $(this).parent().parent().find('#hostgroup_id').text();
            group_list.push(group);
        }
    });
    var h_list = String(host_list);
    var g_list = String(group_list);
    $.ajax({
        url: '/cmdb/host/manage.html',
        type: 'POST',
        data: {"host_list": h_list, 'group_list': g_list},
        dataType: 'json',
        headers: {'X-CSRFtoken': $.cookie('csrftoken')},
        success: function (data) {
            flag = data['flag'];
            msg = data['msg'];
            if (flag){
                alert('删除成功');
                location.reload();
            }
            else
                alert(msg);
        },
        error: function (data) {
            alert(data);
        }
    });

});