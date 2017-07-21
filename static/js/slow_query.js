/**
 * Created by Administrator on 2017/7/21.
 */
$(function () {
    $(".show_sql").each(function(){
        $(this).click(function () {
            $(this).parent().parent().next().toggleClass('hidden');
        })
    });
});