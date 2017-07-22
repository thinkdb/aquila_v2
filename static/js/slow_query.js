/**
 * Created by Administrator on 2017/7/21.
 */
$(function () {
    // 查看sql 文本
    $(".show_sql").each(function(){
        $(this).click(function () {
            $(this).parent().parent().next().toggleClass('hidden');
        })
    });

    // 查看慢sql相关表详情
    $('.show_query_rely').each(function () {
        $(this).click(function () {
            $(this).next().toggleClass('hidden');
        })
    })
});


