$(function () {
    $('button').click(function () {
        var name = $("#uname").val();
        var pwd = $("#pwd").val();
        if(name.length == 0|| pwd.length ==0){
            alert("用户名或密码不能为空");
            return
        }
        var enc_pwd = md5(pwd);
        $.ajax({
            url:'/api/client/v1/login/',
            data:{
                uname:name,
                password:enc_pwd,
            },
            method:"post",
            success:function (res) {
                if(res.code == 0){
                    window.open(res.data,target='_self')
                }else {
                    alert(res.msg)
                }
            }
        })

    })
});