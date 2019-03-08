$(function () {
    var types_menu_is_down = true;
    var sort_menu_is_down = true;
    $("#all_type").click(function () {
        sub_type_toggle()
    });
    $('#sub_types').click(function () {
        sub_type_toggle()
    });
    $('#all_sort').click(function () {
        sort_toggle()
    });
    $('#sort').click(function () {
        sort_toggle()
    });
    function sub_type_toggle() {
        $('#sub_types').toggle();
        if(types_menu_is_down){
            $("#all_type").find("span").find("span").removeClass("glyphicon glyphicon-menu-down").addClass("glyphicon glyphicon-menu-up");
            types_menu_is_down = false;
        }else {
            $("#all_type").find("span").find("span").removeClass("glyphicon glyphicon-menu-up").addClass("glyphicon glyphicon-menu-down");
            types_menu_is_down = true;
        }
    }
    function sort_toggle() {
        $('#sort').toggle();
        if(sort_menu_is_down){
            $("#all_sort").find("span").find("span").removeClass("glyphicon glyphicon-menu-down").addClass("glyphicon glyphicon-menu-up");
            sort_menu_is_down = false;
        }else {
            $("#all_sort").find("span").find("span").removeClass("glyphicon glyphicon-menu-up").addClass("glyphicon glyphicon-menu-down");
            sort_menu_is_down = true;
        }
    }


    // 商品添加到购物车
    $('.addShopping').click(function () {
        //要知道商品的id
        var goods_id = $(this).attr("goods_id");
        var $current_btn = $(this);
        // console.log(goods_id)
        //发送请求
        $.ajax({
            url:'/api/client/v1/cart-item/',
            data:{
                goods:goods_id,
                num:1,
            },
            method:'post',
            success:function (res) {
                if(res.code == 1){
                    //没登录
                    window.open(res.data,target="_self")
                }else if(res.code==0){
                    $current_btn.prev().html(res.data.num)
                }else {
                    alert(res.data.msg)
                }
            }


        })
        //如果成功要更新商品显示的数量
        //如果没登录 我们要跳转到登录页面
    });
    $('.subShopping').click(function () {
        //要知道商品的id
        var goods_id = $(this).attr("goods_id");
        var $current_btn = $(this);
        // console.log(goods_id)
        // 如果当前显示的数量是0那么就不发送请求
        if ($current_btn.next().text() == "0"){
            return
        }
        //发送请求
        $.ajax({
            url:'/api/client/v1/cart-item/',
            data:{
                goods:goods_id,
                num:1,
            },
            method:'put',
            success:function (res) {
                if(res.code == 1){
                    //没登录
                    window.open(res.data,target="_self")
                }else if(res.code==0){
                    $current_btn.next().html(res.data)
                }else {
                    alert(res.data.msg)
                }
            }


        })
        //如果成功要更新商品显示的数量
        //如果没登录 我们要跳转到登录页面
    });
});