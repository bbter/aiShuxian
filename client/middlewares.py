import datetime
from .tasks import *
from django.conf import settings
from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from .models import Exceptions


class MyMiddleware(MiddlewareMixin):
    def process_exception(self,request,exception):
        if settings.DEBUG == False:
            schema = "https//" if request.is_secure() else "http://"
            url_path = request.path
            url = "{schema}{host_and_port}{url_path}".format(
                host_and_port=request.get_host(),
                url_path=url_path,
                schema=schema
            )
            today = datetime.date.today()
            print(url)
            print(today)
            print(exception)
            error = Exceptions.objects.filter(path=url,date=today,error_msg=exception)
            # print(error[0].count)
            if not error:
                Exceptions.objects.create(
                    path=url,
                    date=today,
                    error_msg=exception
                )
                error1 = Exceptions.objects.filter(path=url, date=today, error_msg=exception)
                url_msg = error1[0].path
                error_msg = error1[0].error_msg
                send_mail_task.delay(error_msg, url_msg)
            else:
                count = error[0].count + 1
                error[0].count = count
                error[0].save()

                if error[0].count == 10:
                    print("xxx")
                    url_msg = error[0].path
                    error_msg = error[0].error_msg
                    send_mail_task.delay(error_msg,url_msg)
        #发个邮件
        res = {
            'code':10,
            'msg':str(exception),
            'data':''
        }
        return JsonResponse(res)