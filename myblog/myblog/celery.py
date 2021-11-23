from celery import Celery
from django.conf import settings
import os

# 
os.environ.setdefault("DJANGO_SETTINGS_MODULE",
"myblog.settings")


app = Celery("myblog")
# 参数配置
app.conf.update(
    BROKER_URL = "redis://:@127.0.0.1:6379/1"
)

# 自动去已注册的应用下找加载worker函数
app.autodiscover_tasks(settings.INSTALLED_APPS)