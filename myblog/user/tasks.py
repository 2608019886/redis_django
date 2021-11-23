from myblog.celery import app
from tools.sms import YunTongXin
from django.conf import settings

@app.task
def send_sms_c(phone, code):
    config = settings.SMS_CONFIG
    a = YunTongXin(**config)
    res = a.run(phone, code)

    return res