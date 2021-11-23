from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from user.models import UserProfile
from tools.logging_dec import logging_check
from django.core.cache import cache
from tools.sms import YunTongXin
from django.conf import settings
from .tasks import send_sms_c
import json, hashlib, random

# 异常码 10100 - 10199

# django提供的装饰器  method_decorator , 可以将函数装饰器转换为  方法装饰器

# Create your views here.
# FBV
@logging_check
def users_views(request, username):
    if request.method != "POST":
        result = {"code": 10103, "error": "请使用POST请求！"}
        return JsonResponse(result)
    
    user = request.myuser
    
    avatar = request.FILES["avatar"]
    user.avatar = avatar
    user.save()
    return JsonResponse({"code": 200})

def sms_view(request):
    if request.method != "POST":
        result = {"code": 10104, "error": "请使用POST请求！"}
        return JsonResponse(result)
    json_str = request.body
    json_obj = json.loads(json_str)
    phone = json_obj["phone"]
    if len(phone) != 11:
        result = {"code": 10105, "error": "请输入正确的手机号！"}
        return JsonResponse(result)
    # 生成随机码
    code = random.randint(1000, 9999)
    # print(code)
    # 存储随机码
    cache_key  = f"sms_{phone}"
    # 检查是否存在已发送过且未过期的验证码
    old_code = cache.get(cache_key)
    if old_code:
        result = {"code": 10108, "error": "请勿重复发送！"}
        return JsonResponse(result)
    cache.set(cache_key, code, 60 * 3)
    # 发生
    # celery
    # res = json.loads(send_sms(phone, code))
    # if res["statusCode"] == "000000":
    #     return JsonResponse({"code": 200})
    # else:
    #     result = {"code": 10105, "error": "验证码发送异常！"}
    #     return JsonResponse(result)
    send_sms_c.delay(phone, code)
    return JsonResponse({"code": 200})

def send_sms(phone, code):
    config = settings.SMS_CONFIG
    a = YunTongXin(**config)
    res = a.run(phone, code)

    return res
# CBV
# 更灵活[可继承]
# 对未定义的http method请求 直接返回405响应
class UserViews(View):

    def get(self, request, username=None):
        # /v1/users
        # /v1/users/username
        if username:
            # /v1/users/username
            try:
                user = UserProfile.objects.get(username=username)
            except Exception as e:
                result = {"code": 10102, "error": "用户不存在！"}
                return JsonResponse(result)
            data = {
                "info": user.info,
                "sign": user.sign,
                "nickname": user.nickname,
                "avatar": str(user.avatar)
            }
            result = {"code": 200, "username": username, "data": data}
            return JsonResponse(result)
        else:
             return JsonResponse({"code": 200, "msg": "无get请求"})

       
    def post(self, request):

        # 获取传入的参数
        json_str = request.body
        json_obj = json.loads(json_str)
        username = json_obj["username"]
        email = json_obj["email"]
        password_1 = json_obj["password_1"]
        password_2 = json_obj["password_2"]
        phone = json_obj["phone"]
        sms_num = json_obj["sms_num"]

        # 参数基本检查
        if password_1 != password_2:
            result = {"code": 10100, "error": "密码不一致！"}
            return JsonResponse(result)
        # 验证码检查
        old_code = cache.get(f"sms_{phone}")
        if not old_code:
            result = {"code": 10106, "error": "验证码错误！"}
            return JsonResponse(result)
        if int(sms_num) != old_code:
            result = {"code": 10106, "error": "验证码错误！"}
            return JsonResponse(result)
        cache.set(f"sms_{phone}","",0)
        # 用户名是否可用
        old_users = UserProfile.objects.filter(username=username)
        if old_users:
            result = {"code": 10101, "error": "用户名已存在"}
            return JsonResponse(result)

        # 插入用户数据
        p_m = hashlib.md5()
        # 需要转为字节串
        p_m.update(password_1.encode())

        UserProfile.objects.create(
            username=username, 
            nickname=username, 
            password=p_m.hexdigest(), 
            email=email, 
            phone=phone
        )

        result = {"code": 200, "username": username, "data": {}}
        return JsonResponse(result)


    @method_decorator(logging_check)
    def put(self, request, username=None):
        # 更新用户数据[昵称， 个人签名，个人描述]
        json_str = request.body
        json_obj = json.loads(json_str)
        
        user = request.myuser
        
        user.sign = json_obj["sign"]
        user.info = json_obj["info"]
        user.nickname = json_obj["nickname"]

        user.save()
        return JsonResponse({"code": 200}) 