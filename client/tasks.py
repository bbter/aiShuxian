from celery import task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import get_template




@task
def send_verify_email(email,url):
    title = "激活邮件"
    msg = "注册邮件"
    recievies = [email]
    template = get_template("mail.html")
    html_str = template.render({"url": url,})
    send_mail(
        title,
        msg,
        settings.DEFAULT_FROM_EMAIL,
        recievies,
        html_message=html_str
    )


@task
def send_mail_task(error,url_msg):
    title = "错误信息"
    msg = ""
    recievies = ['1035675608@qq.com', '409708306@qq.com']
    template = get_template("mail1.html")
    html_str = template.render({"url": url_msg,"error":error})
    send_mail(
        title,
        msg,
        settings.DEFAULT_FROM_EMAIL,
        recievies,
        html_message=html_str
    )