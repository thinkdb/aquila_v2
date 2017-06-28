/**
 * Created by Administrator on 2017/6/28.
 */
$(function () {
    $('.host_list').change(function () {
        console.log(1);
    });


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
                update_table_info(table_info);
            },
            error: function(data){
                console.log(data);
            }
        })
    });
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
});