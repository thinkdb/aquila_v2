/**
 * Created by Administrator on 2017/6/28.
 */
$(function () {
    function schema_obj (cs) {
        $('.'+cs).change(function () {
            var db_name = $('.db_list').val();
            var host_ip = $('.host_list').val();
            $.ajax({
                url: '/dbms/metadata/metadata_info.html',
                type: 'GET',
                data: {'host_ip': host_ip, 'table_schema': db_name},
                dataType: 'JSON',
                success: function (data) {
                    if (cs == 'host_list'){
                        updated_db_info(data);
                    }else{
                        updated_table_info(data);
                    }
                },
                error: function(data){
                    console.log(data);
                }
            })
        })
    }

    schema_obj('host_list');
    schema_obj('db_list');


    // 选择表后,触发查询获取表相关信息

    $('.table_list').change(function () {
        var host_ip = $('.host_list').val();
        var table_schema = $('.db_list').val();
        var table_name = $('.table_list').val();
        console.log(host_ip, table_schema, table_name);
        $.ajax({
            url: '/dbms/metadata/get_table_info.html',
            type: 'GET',
            data: {'host_ip': host_ip, 'table_schema': table_schema, 'table_name': table_name},
            dataType: 'JSON',
            success: function (data) {
                table_info = data.table_info;
                column_info = data.column_info;
                index_info = data.index_info;
                table_sc = data.table_sc;
                update_table_info(table_info);
            },
            error: function(data){
                console.log(data);
            }
        })
    });

    // 填充库信息
    function updated_db_info(data) {
        $('.db_list .db_option').nextAll().remove();
        if(data.db_info.length > 0){
            for (item in data.db_info) {
                var option_obj = document.createElement('option');
                option_obj.innerText = data.db_info[item];
                $('.db_list .db_option').after(option_obj);
            }

        }

    }

    // 填充表信息
    function updated_table_info(data) {
        $('.table_list .table_option').nextAll().remove();
        console.log(11111);
        if(data.table_info.length > 0){
            for (item in data.table_info) {
                var option_obj = document.createElement('option');
                option_obj.innerText = data.table_info[item];
                $('.table_list .table_option').after(option_obj);
            }

        }

    }

    // 填充表相关信息
    function update_table_info(data) {
        $('#table_info #table_name').text(data.table_name);
        $('#table_info #engine').text(data.engine);
        $('#table_info #row_format').text(data.row_format);
        $('#table_info #table_rows').text(data.table_rows);
        $('#table_info #avg_row_length').text(data.avg_row_length);
        $('#table_info #max_data_length').text(data.max_data_length);
        $('#table_info #data_length').text(data.data_length);
        $('#table_info #index_length').text(data.index_length);
        $('#table_info #data_free').text(data.data_free);
        $('#table_info #chip_size').text(data.chip_size);
        $('#table_info #auto_increment').text(data.auto_increment);
        $('#table_info #table_collation').text(data.table_collation);
        $('#table_info #create_time').text(data.create_time);
        $('#table_info #check_time').text(data.check_time);
        $('#table_info #update_time').text(data.update_time);
        $('#table_info #table_comment').text(data.table_comment);
    }

    // 填充列信息
    function update_column_info(data) {
        
    }
});