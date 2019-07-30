import markdown
from django.shortcuts import render  # 用模板页面输出我们的系统响应
from django.core.paginator import Paginator  # Django自带的分页器
from django.shortcuts import get_object_or_404  # 这个方法返回找不到的页面
from django.db.models import Count
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from read_statistics.utils import read_statistics_once_read
from .models import Blog, BlogType


# 博客列表中共同的数据
def get_blog_list_common_data(blogs_all_list, request):
    paginator = Paginator(blogs_all_list, settings.BLOGS_NUM_PAGE)
    page_num = request.GET.get('page', 1)  # 获取页码参数（GET请求）
    try:
        page_of_blogs = paginator.page(int(page_num))
    except Exception:
        page_of_blogs = paginator.page(1)
    currentr_page_num = page_of_blogs.number  # 获取当前页码
    page_range = list(range(max(currentr_page_num - 2, 1), currentr_page_num)) + list(range(currentr_page_num, min(currentr_page_num + 2, paginator.num_pages) + 1))
    # 加上省略页码标记
    if page_range[0] > 2:
        page_range.insert(0, '...')
    if page_range[-1] < paginator.num_pages - 1:
        page_range.append('...')
    # 加上首页和尾页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    # 获取博客分类后的数量
    # BlogType.objects.annotate(blog_count=Count('blog'))
    """
    blog_types_list = []
    blog_types = BlogType.objects.all()
    for blog_type in blog_types:
        blog_type.blog_count = BlogType.objects.filter(blog_type=blog_type).count()
        blog_types_list.append(blog_type)
    """
    # 获取时间分类对应的博客数量
    blog_dates = Blog.objects.dates('created_time', 'month', order='DESC')
    blog_dates_dict = {}
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(created_time__year=blog_date.year, created_time__month=blog_date.month).count()
        blog_dates_dict[blog_date] = blog_count

    context = {}
    context['blogs'] = page_of_blogs.object_list
    context['page_of_blogs'] = page_of_blogs
    # context['blogs_count'] = Blog.objects.all().count()  # 可用于统计博客数量
    context['blog_types'] = BlogType.objects.annotate(blog_count=Count('blog'))
    context['page_range'] = page_range
    context['blog_dates'] = blog_dates_dict
    return context


# 访问blog的列表
def blog_list(request):
    blogs_all_list = Blog.objects.all()
    context = get_blog_list_common_data(blogs_all_list, request)
    return render(request, 'blog/blog_list.html', context)


# 显示博客分类
def blogs_with_type(request, blog_type_pk):
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    blogs_all_list = Blog.objects.filter(blog_type=blog_type)
    context = get_blog_list_common_data(blogs_all_list, request)
    context['blog_type'] = blog_type
    return render(request, 'blog/blogs_with_type.html', context)


# 按年月来对博客进行分类
def blogs_with_date(request, year, month):
    blogs_all_list = Blog.objects.filter(created_time__year=year, created_time__month=month)
    context = get_blog_list_common_data(blogs_all_list, request)
    context['blog_with_date'] = '%d年%d月' % (year, month)
    return render(request, 'blog/blogs_with_date.html', context)


# 显示具体的博客页面
def blog_detail(request, blog_pk):
    blog = get_object_or_404(Blog, pk=blog_pk)
    blog.content = markdown.markdown(blog.content.replace("\r\n", '  \n'), extensions=[
        'markdown.extensions.extra',
        'markdown.extensions.codehilite',
        'markdown.extensions.toc',
    ], safe_mode=True,enable_attributes=False)
    read_cookie_key = read_statistics_once_read(request, blog)

    context = {}
    context['previous_blog'] = Blog.objects.filter(created_time__gt=blog.created_time).last()
    context['next_blog'] = Blog.objects.filter(created_time__lt=blog.created_time).first()
    context['blog'] = blog
    response = render(request, 'blog/blog_detail.html', context)  # 响应
    response.set_cookie(read_cookie_key, 'true')  # 让浏览器保存相应的数据
    return response
