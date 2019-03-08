from __future__ import absolute_import
from celery import Celery
import os

from django.conf import settings

os.environ.setdefault("DJANGO_SETTING_MODULE", "axf.settings")


app = Celery("mycelery")

app.conf.timezone = "Asia/Shanghai"

#指定celery的配置来源 用的是项目的配置文件settings.py
app.config_from_object("django.conf:settings")

app.autodiscover_tasks(lambda : settings.INSTALLED_APPS)