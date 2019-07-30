from django.contrib import admin
from .models import BlogType, Blog  # 导入当前项目里的模型,装饰器用于模型管理的注册


@admin.register(BlogType)
class BlogTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'type_name')


@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'blog_type',
        'author', 'get_read_num',
        'created_time', 'last_updated_time'
        )
