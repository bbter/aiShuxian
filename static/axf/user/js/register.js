$(function () {
    $("button").click(function () {
        // 获取全部的数据
        var name = $('#uname').val();
        var pwd = $('#pwd').val();
        var confirm_pwd = $('#confirm_pwd').val();
        var email = $('#email').val();
        var file = $('#icon')[0].files[0];
        // 数据校验
        if(pwd != confirm_pwd){
            alert("密码和确认密码不一致");
            return
        }
        // 做md5摘要
        var enc_pwd = md5(pwd);
        var enc_confirm_pwd = md5(confirm_pwd);
        if(file.size==0){
            alert("请选择头像");
            return
        }
        var formdata = new FormData();
        formdata.append("username",name);
        formdata.append("password",enc_pwd);
        formdata.append("confirm_pwd",enc_confirm_pwd);
        formdata.append("email",email);
        formdata.append("icon",file);


        // 上传数据
        $.ajax({
            url:'/api/client/v1/register/',
            data:formdata,
            processData:false,
            cache:false,
            contentType:false,
            method:"post",
            success:function (res) {
                console.log(res);
                if(res.code == 0){
                    window.open(res.data,target='_self')
                }else{
                    alert(res.msg)
                }
            }
        })
    });
    var error_p = $("<p style='color: red;display: none'></p>");
    $("#uname").after(error_p);
    $("#uname").change(function () {
        var name = $("#uname").val();
        if(name.length<3){
            error_p.html("用户名过短");
            error_p.attr('style','color: red;display: block');
            return
        }
        else {
            error_p.attr('style','color: red;display: none');
        }
        $.ajax({
            url:'/api/client/v1/check/',
            data:{
                uname:name,
            },
            method: 'post',
            success:function (res) {
                if(res.code==1){
                    error_p.html(res.msg);
                    error_p.attr('style','color: red;display: block');
                }
                else {
                    error_p.attr('style','color: red;display: none');
                }
            }
        })
    })
});