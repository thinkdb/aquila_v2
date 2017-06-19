/**
 * Created by Administrator on 2017/6/19.
 */
$(function () {
    $('#work_info').each(function () {
        $('#work_order_id').click(function () {
            $(this).parent().next().toggleClass('detail_close');
        })
    })
});


// $(function () {
//     console.log($(this).parent().next());
// })