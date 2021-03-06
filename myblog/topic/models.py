from django.db import models
from user.models import UserProfile

# Create your models here.
class Topic(models.Model):
    title = models.CharField(verbose_name="文章标题", max_length=50)
    category = models.CharField(verbose_name="文章分类", max_length=20)
    limit = models.CharField(verbose_name="文章权限", max_length=20)
    introduce = models.CharField(verbose_name="文章简介", max_length=90)
    content = models.TextField(verbose_name="文章内容")
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    author_id = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
