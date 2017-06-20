/**
 * Created by Administrator on 2017/6/19.
 */
$(function () {

    function WorkCommit(button_name, url, msg){
        $('tbody .'+button_name).each(function(){
            $(this).click(function(){
                $.ajax({
                    url: url,
                    type: 'POST',
                    data: {'wid': $(this).parent().parent().find('#work_order_id').text(), 'flag': $(this).val()},
                    dataType: 'JSON',
                    success: function(data){
                        status = data.status;
                        err_msg = data.error_msg;

                        if(status==1){
                            alert(msg);

                        }
                        else{
                            alert(err_msg);
                        }

                    },
                    error: function(data){
                        console.log(data);
                    }
                    })
            })
        });
    }

    function csrfSafeMethod(method) {
        // these HTTP methods do not require CSRF protection
       return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
    }


    $.ajaxSetup({
        beforeSend:function (xhr, settings) {
            if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader('X-CSRFtoken', $.cookie('csrftoken'));
            }
        }
    });

    $('tbody #work_info #work_order_id').each(function () {
        $(this).click(function () {
                $(this).parent().next().toggleClass('detail_close');
        })
    });

    WorkCommit('audit_button', '/dbms/sql_publish/sql-audit.html', '提交成功');
    WorkCommit('run_button', '/dbms/sql_publish/sql-running.html', '任务已经提交到后台执行，请《工单查询》页面查看进度');
});