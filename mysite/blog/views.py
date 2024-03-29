from django.shortcuts import render_to_response, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Count
from .models import Blog,BlogType
from read_statist.utils import read_statist_once_read

def get_blogs_list_commone_date(request, blogs_all_list):
    blogs_all_list = Blog.objects.all()
    paginator = Paginator(blogs_all_list, 5)#每()pian进行分页
    page_num = request.GET.get('page', 1)# 获取url的页面参数（GET请求）
    page_of_blogs = paginator.get_page(page_num)
    currentr_page_num =  page_of_blogs.number##获取当前页码
    #对页码多余部分的处理
    page_range = list(range(max(currentr_page_num - 2, 1 ), currentr_page_num)) + \
                 list(range(currentr_page_num, min(currentr_page_num +2, paginator.num_pages) +1))
    #页码优化

    #省略标记
    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    #首页和尾页
    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)
    #加上省略页码标记

    #获取博客分类对应的博客数量
    BlogType.objects.annotate(blog_count = Count('blog'))

    '''
    blog_types = BlogType.objects.all()
    blog_types_list = []
    for blog_type in blog_types:
        blog_type.blog_count = Blog.objects.filter(blog_type=blog_type).count()
    '''
    # 获取日期归档对应的博客数量
    blog_dates = Blog.objects.dates('created_time', 'month', order="DESC")
    blog_dates_dict = {} #字典存放
    for blog_date in blog_dates:
        blog_count = Blog.objects.filter(created_time__year=blog_date.year,
                                         created_time__month=blog_date.month).count()
        blog_dates_dict[blog_date] = blog_count

    context = {}
    context['blogs'] = page_of_blogs.object_list
    context['page_of_blogs'] = page_of_blogs
    context['page_range'] = page_range
    context['blog_types'] = BlogType.objects.annotate(blog_count = Count('blog'))
    context['blog_dates'] = blog_dates_dict
    return context

def blog_list(request):
    context = get_blogs_list_commone_date(request, blog_list)
    return render_to_response('blog/blog_list.html', context)

def blog_detail(request, blog_pk):
    blog = get_object_or_404(Blog, pk=blog_pk)
    read_cookie_key = read_statist_once_read(request, blog)

    context = {}
    context['previous_blog']  = Blog.objects.filter(created_time__gt=blog.created_time).last()
    context['next_blog'] = Blog.objects.filter(created_time__lt=blog.created_time).first()
    context['blog'] = blog
    response = render_to_response('blog/blog_detail.html', context)#响应
    response.set_cookie(read_cookie_key, 'true')
    return response

def blogs_with_type(request, blog_type_pk):
    context = {}
    context = get_blogs_list_commone_date(request, blog_list)
    blog_type = get_object_or_404(BlogType, pk=blog_type_pk)
    blogs_all_list = Blog.objects.filter(blog_type=blog_type_pk)
    return render_to_response('blog/blogs_with_type.html',context)

def blogs_with_date(request, year, month):
    context = {}
    context = get_blogs_list_commone_date(request, blog_list)
    blogs_all_list = Blog.objects.filter(created_time__year=year, created_time__month=month)
    return render_to_response('blog/blogs_with_date.html',context)
