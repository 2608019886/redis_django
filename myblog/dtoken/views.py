from django.shortcuts import render
from django.http import JsonResponse
from user.models import UserProfile
from django.conf import settings
import json, hashlib, time, jwt


# Create your views here.
def tokens(requests):
    # 检验请求方法
    if requests.method != "POST":
        result = {"code": 10200, "error": "请使用POST请求！"}
        return JsonResponse(result)
    # 获取上传数据
    json_str = requests.body
    json_obj = json.loads(json_str)
    username = json_obj["username"]
    password = json_obj["password"]
    # 检验用户名和密码
    try: 
        user = UserProfile.objects.get(username=username)
    except Exception as e:
        result = {"code": 10201, "error": "用户名或密码错误！"}
        return JsonResponse(result)
    md5 = hashlib.md5()
    md5.update(password.encode())
    if md5.hexdigest() != user.password:
        result = {"code": 10202, "error": "用户名或密码错误！"}
        return JsonResponse(result)

    # 记录会话
    token = make_token(username)
    result = {"code": 200, "username": username, "data": {"token": token}}
    return JsonResponse(result)


def make_token(username, expire=3600*24):
    key = settings.JWT_TOKEN_KEY
    now_t = time.time()
    payload_data = {"username": username, "exp": now_t + expire}
    return jwt.encode(payload_data, key, algorithm="HS256")