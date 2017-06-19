/**
 * Created by Administrator on 2017/6/19.
 */
$(function () {

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

    $('tbody .audit_button').each(function(){
        $(this).click(function(){
            $.ajax({
                url: '/dbms/sql_publish/sql-audit.html',
                type: 'POST',
                data: {'wid': $(this).parent().parent().find('#work_order_id').text(), 'flag': $(this).val()},
                dataType: 'JSON',
                success: function(data){
                    status = data.status;
                    err_msg = data.data;
                    if(status){
                        alert('提交成功');
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

    $('tbody .run_button').each(function(){
        $(this).click(function(){
            $.ajax({
                url: '/dbms/sql_publish/sql-running.html',
                type: 'POST',
                data: {'wid': $(this).parent().parent().find('#work_order_id').text(), 'flag': $(this).val()},
                dataType: 'JSON',
                success: function(data){
                    status = data.status;
                    err_msg = data.data;

                    if(status==1){
                        alert('提交成功');
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
});

