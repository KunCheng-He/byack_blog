from django.db import models
from django.contrib.auth.models import User  # django自带的用户系统
from django.contrib.contenttypes.fields import GenericRelation
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField  # 引入富文本编辑器,并加入上传图片
from mdeditor.fields import MDTextField
from read_statistics.models import ReadNumExpandMethod, ReadDetail


# 博客分类
class BlogType(models.Model):
    """
    博客类型也是字符串，用文本类型，不会太长，最大长度不超过15
    """
    type_name = models.CharField(max_length=15)

    def __str__(self):
        return self.type_name


# 博文
class Blog(models.Model, ReadNumExpandMethod):
    """
    博文标题，用文本类型的字段，最大长度不超过50
    博客分类，是一个外键，关联到BlogType模型，设置删除行为，删除博文不要删除博客类型
    内容不知道有多长，使用长文本这个字段
    作者是一个外键，关联到User这个模型，删除不需要执行什么操作
    创建时间，自动的添加当前时间
    最后跟新时间
    """
    title = models.CharField(max_length=50)
    blog_type = models.ForeignKey(BlogType, on_delete=models.CASCADE)
    content = MDTextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    read_details = GenericRelation(ReadDetail)
    created_time = models.DateTimeField(auto_now_add=True)
    last_updated_time = models.DateTimeField(auto_now=True)

    def get_url(self):
        return reverse('blog_detail', kwargs={'blog_pk': self.pk})
    
    def get_email(self):
        return self.author.email

    def __str__(self):
        return "<Blog: %s>" % self.title

    class Meta:
        ordering = ['-created_time']
