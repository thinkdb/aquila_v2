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
            if (self.find('.w-progress-bar')){
                get_progress(self);
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
    function get_progress(self) {
        var sql_hash_str = '';
        self.parent().next().find('#sql_hash').each(function () {
            var a = $(this).text();
            sql_hash_str = sql_hash_str.concat(a);
        });
        if (self.parent().next().attr('class') != 'detail_close') {
            $.ajax({
                url: '/dbms/sql_publish/sql-progress.html',
                type: 'GET',
                data: {'sql_hash': sql_hash_str},
                dataType: 'JSON',
                success: function (data) {
                    // data = {'wid':'', 'per': '', 'time_consuming': '', 'ptosc_flag': 0, 'wid_status': 1}
                    var wid_status = data.wid_status;
                    var ptosc_flag = data.ptosc_flag;
                    var per = data.per;
                    var wid = data.wid;
                    var time_consuming = data.time_consuming;
                    if (ptosc_flag > 0 && wid_status > 1) {
                        if (wid) {
                            var pro_bar = self.parent().next().find('#' + wid);
                            if (per == 100) {
                                pro_bar.children('span').find('.w-progress-bar').text(per);
                                pro_bar.attr('style', 'width: ' + per + '%');
                                pro_bar.parent().parent().next().find('.time_consuming').text(time_consuming);
                                pro_bar.removeClass("active");
                            }
                        }
                    }
                    else {
                        alert('数据异常，请联系管理员');
                    }
                },
                error: function (data) {
                    console.log(data);
                    alert('请求异常, 请联系管理员')
                }
            });
            setTimeout(get_progress(self), 1000);
        }
    }
});
