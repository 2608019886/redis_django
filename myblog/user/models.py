from django.db import models
import random


def default_sign():
    return "签名是一种艺术"

# Create your models here.
class UserProfile(models.Model):
    username = models.CharField(verbose_name="用户名", max_length=11, primary_key=True)
    nickname = models.CharField(max_length=30, verbose_name="昵称")
    password = models.CharField(max_length=32)
    phone = models.CharField(max_length=11)
    email = models.EmailField(default="")
    avatar = models.ImageField(upload_to="avatar", null=True)
    sign = models.CharField(max_length=50, verbose_name="个人签名", default=default_sign)
    info = models.CharField(max_length=150, verbose_name="个人简介", default="")
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "user_user_profile"