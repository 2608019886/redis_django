# 登陆装饰器
from django.conf import settings
from django.http import JsonResponse
from user.models import UserProfile
import jwt


def logging_check(func):
    def wrapper(request, *args, **kwargs):
        # 获取token request.META.get("HTTP_AUTHORIZATION")
        token = request.META.get("HTTP_AUTHORIZATION")
        if not token:
            result = {"code": 403, "error": "请先登录！"}
            return JsonResponse(result)
        # 校验token   
        try:
            res = jwt.decode(token, settings.JWT_TOKEN_KEY, algorithms="HS256")
        except Exception as e:
            result = {"code": 403, "error": "请先登录！"}
            return JsonResponse(result)
        # 失败返回403

        # 用户传递
        user = UserProfile.objects.get(username=res["username"])
        request.myuser = user

        return func(request, *args, **kwargs)
    return wrapper


def get_user_by_request(request):
    # 尝试性获取登录用户
    token = request.META.get("HTTP_AUTHORIZATION")
    if not token:
        return None
    try:
        res = jwt.decode(token, settings.JWT_TOKEN_KEY, algorithms="HS256")
    except Exception as e:
        return None
    
    username = res["username"]

    user = UserProfile.objects.get(username=username)
    return user