# 缓存
from .logging_dec import get_user_by_request
from django.core.cache import cache


def cache_set(expire):
    """可传参的缓存装饰器

    Args:
        expire ([type]): 缓存时间
    """
    def _cache_set(func):
        def wrapper(request, *args, **kwargs):
            # 区分场景 - 只做列表页
            if "t_id" in request.GET:
                # 获取详情页
                 return func(request, *args, **kwargs)
            
            # 生成正确的 cache key [访客访问 和 自身访问]
            visitor_user = get_user_by_request(request)
            visitor_username = None
            if visitor_user:
                visitor_username = visitor_user.username
            author_username = kwargs["author_id"]

            full_path = request.get_full_path()
            
            if visitor_username == author_username:
                # 自身访问
                print("-- self in --")
                cache_key = "topics_cache_self_%s"%(full_path)
            else:
                # 访客访问
                print("-- other in --")
                cache_key = "topics_cache_%s"%(full_path)
            # 判断是否有缓存  有则直接返回
            cache_res = cache.get(cache_key)
            if cache_res:
                print("-- cache in --")
                return cache_res
            # 执行视图
            res = func(request, *args, **kwargs)
            # 存储缓存  cache对象/set/get
            print("-- cache set --")
            cache.set(cache_key, res, expire)
            # 返回响应
            return res
        return wrapper
    return _cache_set