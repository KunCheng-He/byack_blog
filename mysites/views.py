import datetime
from django.shortcuts import render, redirect  # 第二个是重定向的方法
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.db.models import Sum
from django.core.cache import cache  #　缓存表
from django.contrib import auth
from django.urls import reverse  # 反向解析，通过网页别名，解析出url
from read_statistics.utils import get_saven_days_read_date, get_today_hot_data, get_yesterday_hot_data
from blog.models import Blog



# 获取前７天的阅读数据
def get_7_days_hot_blogs():
    today = timezone.now().date()
    date = today - datetime.timedelta(days=7)
    blogs = Blog.objects.filter(read_details__date__lt=today, read_details__date__gte=date).values('id', 'title').annotate(read_num_sum=Sum('read_details__read_num')).order_by('-read_num_sum')  # 先筛选出对应的日期，然后对博客进行分组，然后求和再排序
    return blogs[:7]


def home(request):
    blog_content_type = ContentType.objects.get_for_model(Blog)
    dates, read_nums = get_saven_days_read_date(blog_content_type)
    today_hot_data = get_today_hot_data(blog_content_type)
    yesterday_hot_data = get_yesterday_hot_data(blog_content_type)

    # 对７天热门博客的缓存数据
    hot_data_7_blogs = cache.get('hot_data_7_blogs')
    if hot_data_7_blogs is None:
        hot_data_7_blogs = get_7_days_hot_blogs()
        cache.set('hot_data_7_blogs', hot_data_7_blogs, 3600)

    context = {}
    context['dates'] = dates
    context['read_nums'] = read_nums
    context['today_hot_data'] = today_hot_data
    context['yesterday_hot_data'] = yesterday_hot_data
    context['hot_data_7_blogs'] = hot_data_7_blogs[:7]
    return render(request, 'home.html', context)
