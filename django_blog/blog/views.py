from datetime import date

from django.db.models import Q, F
from django.views.generic import ListView, DetailView
from django.shortcuts import get_object_or_404
from django.core.cache import cache

from .models import (
    Category,
    Tag,
    Post,
)
from config.models import SideBar


class CommonViewMixin():
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'sidebars': SideBar.get_all(),
        })
        context.update(Category.get_navs())
        return context


class IndexView(CommonViewMixin, ListView):
    '''
    1. 请求到达之后, 会调用 dispatch 进行分发
    2. 调用 get 方法
        (1) get 请求中, 首先调用 get_queryset 方法, 拿到 query_set 中的数据源
        (2) 调用 get_context_data 方法, 拿到需要渲染到模板中的数据
            1) 在 get_context_data 中, 首先调用 get_paginate_by 拿到每页数据
            2) 接着调用 get_context_object_name 拿到要渲染到模板中的这个 queryset 名称
            3) 然后调用 paginate_queryset 进行分页
            4) 最后拿到的数据转为 dict 返回
        (3) 调用 render_to_response 渲染数据到页面中
            1) 在 render_to_response 中调用 get_tempalte_name 拿到模板名
            2) 然后把 request, context, template_name 等传递到模板中

    '''
    queryset = Post.lastest_posts()
    paginate_by = 1
    context_object_name = 'post_list'
    template_name = 'blog/list.html'


class CategoryView(IndexView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_id = self.kwargs.get('category_id')
        category = get_object_or_404(Category, pk=category_id)
        context.update({
            'category': category,
        })
        return context

    def get_queryset(self):
        # 重写 queryset, 根据分类过滤
        queryset = super().get_queryset()
        category_id = self.kwargs.get('category_id')
        return queryset.filter(category_id=category_id)


class TagView(IndexView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        tag_id = self.kwargs.get('tag_id')
        tag = get_object_or_404(Tag, pk=tag_id)
        context.update({
            'tag': tag,
        })
        return context

    def get_queryset(self):
        # 重写 queryset, 根据标签过滤
        queryset = super().get_queryset()
        tag_id = self.kwargs.get('tag_id')
        return queryset.filter(tag__id=tag_id)


class PostDetailView(CommonViewMixin, DetailView):
    queryset = Post.lastest_posts()
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        self.handle_visited()
        return response

    def handle_visited(self):
        increase_pv = False
        increase_uv = False
        uid = self.request.uid
        pv_key = 'pv:%s:%s' % (uid, self.request.path)
        uv_key = 'uv:%s:%s:%s' % (uid, str(date.today()), self.request.path)
        if not cache.get(pv_key):
            increase_pv = True
            cache.set(pv_key, 1, 1*60)  # 一分钟有效

        if not cache.get(uv_key):
            increase_uv = True
            cache.set(uv_key, 1, 24 * 60 * 60)  # 24 小时有效

        if increase_pv and increase_uv:
            Post.objects.filter(pk=self.object.id).update(pv=F('pv') + 1,
                uv=F('uv') + 1)
        elif increase_pv:
            Post.objects.filter(pk=self.object.id).update(pv=F('pv') + 1)
        elif increase_uv:
            Post.objects.filter(pk=self.object.id).update(uv=F('uv') + 1)


class SearchView(IndexView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        context.update({
            'keyword': self.request.GET.get('keyword', '')
        })
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        keyword = self.request.GET.get('keyword')
        if not keyword:
            return queryset
        return queryset.filter(Q(title__icontains=keyword) | Q(desc__icontains=keyword)
                               | Q(content__icontains=keyword))


class AuthorView(IndexView):
    def get_queryset(self):
        queryset = super().get_queryset()
        author_id = self.kwargs.get('owner_id')
        return queryset.filter(owner_id=author_id)