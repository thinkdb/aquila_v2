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
                        var status = data.status;
                        var err_msg = data.error_msg;
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

    $('tbody  #work_order_id').each(function () {
        $(this).click(function () {
            var self = $(this);
            self.parent().prevAll().find('#all_layer').each(function(){
                if ($(this).attr('class') == 'detail_close'){

                }else{
                    $(this).attr('class', 'detail_close');
                }
            });

            self.parent().nextAll().find('#all_layer').each(function(){
                if ($(this).attr('class') == 'detail_close'){

                }else{
                    $(this).attr('class', 'detail_close');
                }
            });
            // $('tbody #all_layer').each(function(){
            //     if($(this).attr('class') == 'detail_close dd') {
            //     }else{
            //         $(this).attr('class', 'detail_close');
            //     }
            // });

            if (self.parent().next().attr('class') == 'detail_close') {
                self.parent().next().toggleClass('detail_close');
            }else {
                self.parent().next().addClass('detail_close');
            }
            var sql_hash = self.parent().next().find('#sql_hash').text();
            if (self.find('.w-progress-bar')){
                get_progress(sql_hash, self);
            }
        })
    });




    $('.rollback_a').each(function(){
            var wid = $(this).parent().parent().find('#work_order_id').text();
            $(this).attr('href','/dbms/rollback/get_rollback-'+wid+'.html');
    });

    WorkCommit('audit_button', '/dbms/sql_publish/sql-audit.html', '提交成功');
    WorkCommit('run_button', '/dbms/sql_publish/sql-running.html', '任务查已经提交到后台执行，请《工单询》页面查看进度');

    // 获取工单进度   
    function get_progress(sql_hash, self) {
        var flag = 1;
        $.ajax({
            url: '/dbms/sql_publish/sql-progress.html',
            type: 'GET',
            data: {'sql_hash': sql_hash},
            dataType: 'JSON',
            success: function (data) {
                var status = data.status;
                var time_con = data.time;
                var per = data.per;
                if (status == 1) {
                    if (self.parent().next().attr('class') == 'detail_close') {
                        flag = 0;
                    }
                    if (flag){
                        if (per) {
                            if (per == 100) {
                                self.parent().next().find('.w-progress-bar').text(per);
                                $('.progress-bar').attr('style', 'width: ' + per + '%');
                                $('.time_consuming').text('0');
                                flag = 0
                            } else {
                                self.parent().next().find('.w-progress-bar').text(per);
                                $('.progress-bar').attr('style', 'width: ' + per + '%');
                                $('.time_consuming').text(time_con);
                                window.setTimeout(get_progress(sql_hash, self), 10000);
                            }
                        } else {
                            flag = 0
                        }
                    }
                }
                else {
                    alert('数据异常，请联系DBA');
                }
            },
            error: function (data) {
                console.log(data);
            }
        });
    }
    // async function get_progress(sql_hash, self){
    //     var flag = 1;
    //     while(flag){
    //         $.ajax({
    //             url: '/dbms/sql_publish/sql-progress.html',
    //             type: 'GET',
    //             data: {'sql_hash': sql_hash},
    //             dataType: 'JSON',
    //             success: function(data){
    //                 var status = data.status;
    //                 var time_con = data.time;
    //                 var per = data.per;
    //
    //                 if(status==1){
    //                     if(per){
    //                         if (per == 100){
    //                             self.parent().next().find('.w-progress-bar').text(per);
    //                             $('.progress-bar').attr('style', 'width: '+ per+'%');
    //                             $('.time_consuming').text('0');
    //                             flag = 0
    //                         }else{
    //                             self.parent().next().find('.w-progress-bar').text(per);
    //                             $('.progress-bar').attr('style', 'width: '+ per+'%');
    //                             $('.time_consuming').text(time_con);
    //                         }
    //                     }else{flag=0};
    //                 }
    //                 else{
    //                     alert('数据异常，请联系DBA');
    //                 }
    //             },
    //             error: function(data){
    //                 console.log(data);
    //             }
    //         });
    //         await sleep(1000);
    //         console.log(self.parent().next().attr('class') );
    //         if (self.parent().next().attr('class') == 'detail_close'){
    //             flag = 0;
    //         }
    //     }
    //
    // }
});
