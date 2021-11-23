from django.shortcuts import render
from django.views import View
from django.utils.decorators import method_decorator
from django.http import JsonResponse
from tools.logging_dec import logging_check, get_user_by_request
from topic.models import Topic
from user.models import UserProfile
import json
from tools.cache_dec import cache_set
from django.core.cache import cache
from message.models import Message

# 异常码 10300 - 10399

# Create your views here.
class TopicViews(View):
    def clear_topics_caches(self, request):
        """清空缓存
        """
        print("-- clear -- ")
        path = request.path_info
        cache_key_p = ["topics_cache_self_", "topics_cache_"]
        cache_key_h = ["", "?category=tec", "?category=no-tec"]
        all_keys = []
        for key_p in cache_key_p:
            for key_h in cache_key_h:
                all_keys.append(key_p + path + key_h)
        cache.delete_many(all_keys)
    def make_topic_res(self, author, author_topic, is_self):
        if is_self:
            # 自身访问
            next_topic = Topic.objects.filter(id__gt=author_topic.id, author_id=author).first()
            last_topic = Topic.objects.filter(id__lt=author_topic.id, author_id=author).last()
        else:
            next_topic = Topic.objects.filter(id__gt=author_topic.id, author_id=author, limit="public").first()
            last_topic = Topic.objects.filter(id__lt=author_topic.id, author_id=author, limit="public").last()
        next_id = next_topic.id if next_topic else None
        next_title = next_topic.title if next_topic else ""
        last_id = last_topic.id if last_topic else None
        last_title = last_topic.title if last_topic else ""

        # 关联留言和回复
        all_messages = Message.objects.filter(topic=author_topic).order_by("-created_time")
        msg_list = []
        rep_dic = {}
        for msg in all_messages:
            if msg.parent_message:
                # 回复
                rep_dic.setdefault(msg.parent_message, [])
                rep_dic[msg.parent_message].append({
                    "msg_id": msg.id, 
                    "publisher": msg.publisher.nickname,
                    "publisher_avatar": str(msg.publisher.avatar),
                    "content": msg.content,
                    "created_time": msg.created_time.strftime("%Y-%m-%d %H:%M:%S")
                })
            else:
                # 留言
                msg_list.append({
                    "id": msg.id, 
                    "content": msg.content,
                    "publisher": msg.publisher.nickname,
                    "publisher_avatar": str(msg.publisher.avatar),
                    "created_time": msg.created_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "reply": []
                })
        for m in msg_list:
            if m["id"] in rep_dic:
                m["reply"] = rep_dic[m["id"]]

        res = {"code": 200, "data": {}}
        res["data"]["nickname"] = author.nickname
        res["data"]["title"] = author_topic.title
        res["data"]["category"] = author_topic.category
        res["data"]["created_time"] = author_topic.created_time.strftime("%Y-%m-%d %H:%M:%S")
        res["data"]["content"] = author_topic.content
        res["data"]["introduce"] = author_topic.introduce
        res["data"]["author"] = author.nickname
        res["data"]["last_id"] = last_id
        res["data"]["last_title"] = last_title
        res["data"]["next_id"] = next_id
        res["data"]["next_title"] = next_title

        
        res["data"]["messages"] = msg_list
        res["data"]["messages_count"] = len(msg_list)
        return res

    def make_topics_res(self, author, author_topics):
        topics_list = []
        for topic in author_topics:
            topic_dic = {}
            topic_dic["id"] = topic.id
            topic_dic["title"] = topic.title
            topic_dic["category"] = topic.category
            topic_dic["created_time"] = topic.created_time.strftime("%Y-%m-%d %H:%M:%S")
            topic_dic["introduce"] = topic.introduce
            topic_dic["author"] = author.username
            topics_list.append(topic_dic)
        # 格式化返回
        return {
            "code": 200,
            "data":{
                "nickname": author.nickname,
                "topics": topics_list
            }
        }

    @method_decorator(cache_set(300))
    def get(self, request, author_id):
        # print("-- view in --")
        try:
            author = UserProfile.objects.get(username=author_id)
        except Exception as e:
            result = {"code": 10301, "error": "用户不存在！"}
            return JsonResponse(result) 
        
        visitor = get_user_by_request(request)
        visitor_username = None
        if visitor:
            visitor_username = visitor.username
        # /v1/topics/user?t_id=1
        t_id = request.GET.get("t_id")
        if t_id:
            # 获取指定文章数据
            t_id = int(t_id)
            is_self = False
            if visitor_username == author_id:
                is_self = True
                # 自身访问
                try:
                    author_topic = Topic.objects.get(id=t_id, author_id=author_id)
                except Exception as e:
                    result = {"code": 10302, "error": "文章不存在！"}
                    return JsonResponse(result)
            else:
                try:
                    author_topic = Topic.objects.get(id=t_id, author_id=author_id, limit="public")
                except Exception as e:
                    result = {"code": 10303, "error": "文章不存在！"}
                    return JsonResponse(result)
            res = self.make_topic_res(author, author_topic, is_self)
            return JsonResponse(res)
        else:
            # 获取列表页数据
            # /v1/topics/user
            # /v1/topics/user?category=[tec/no-tec]
            category = request.GET.get("category")

            if category in ["no-tec", "tec"]:
                if visitor_username == author_id:
                    # 自身访问
                    author_topics = Topic.objects.filter(author_id=author_id, category=category)
                else:
                    author_topics = Topic.objects.filter(author_id=author_id, limit="public", category=category)
            else:
                if visitor_username == author_id:
                    # 自身访问
                    author_topics = Topic.objects.filter(author_id=author_id)
                else:
                    author_topics = Topic.objects.filter(author_id=author_id, limit="public")

            res = self.make_topics_res(author, author_topics)
            
            return JsonResponse(res)

    @method_decorator(logging_check)
    def post(self, request, author_id):
        author = request.myuser
        # 取出前端数据
        json_str = request.body
        json_obj = json.loads(json_str)

        title = json_obj["title"]
        category = json_obj["category"]
        limit = json_obj["limit"]
        introduce = json_obj["content_text"][:30]
        content = json_obj["content"]

        if limit not in ["public", "private"] or category not in ["no-tec", "tec"]:
            result = {"code": 10300, "error": "参数错误！"}
            return JsonResponse(result)

        # 创建topic数据
        Topic.objects.create(
            title=title,
            category=category,
            limit=limit,
            introduce=introduce,
            content=content,
            author_id=author
        )
        # 清空缓存
        self.clear_topics_caches(request)
        return JsonResponse({"code": 200})

    @method_decorator(logging_check)
    def delete(self, request, author_id):
        author = request.myuser
        # /v1/topics/user?t_id=1
        t_id = request.GET.get("t_id")
        if t_id:
            # 获取指定文章数据
            t_id = int(t_id)
            
            try:
                Topic.objects.filter(author_id=author.username, id=t_id).delete()
            except Exception as e:
                result = {"code": 10305, "error": "文章不存在！"}
                return JsonResponse(result)
            res = {"code": 200, "data": "删除成功！"}
            return JsonResponse(res)
        else:
            result = {"code": 10304, "error": "错误请求！"}
            return JsonResponse(result)