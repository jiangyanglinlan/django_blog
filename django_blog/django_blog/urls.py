"""django_blog URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from blog.views import (
    IndexView,
    CategoryView,
    TagView,
    PostDetailView,
    SearchView,
    AuthorView,
)
from comment.views import CommentView
from config.views import LinkListView
from django_blog.custom_site import custom_site


urlpatterns = [
    path('super_admin/', admin.site.urls, name='super-admin'),
    path('admin/', custom_site.urls, name='admin'),

    path('', IndexView.as_view(), name='index'),  # 主页
    path('category/<int:category_id>/', CategoryView.as_view(), name='category-list'),  # 分类
    path('tag/<int:tag_id>/', TagView.as_view(), name='tag-list'),  # 标签
    path('post/<int:post_id>.html', PostDetailView.as_view(), name='post-detail'),  # 文章
    path('search/', SearchView.as_view(), name='search'),  # 搜索
    path('author/<int:owner_id>', AuthorView.as_view(), name='author'),  # 用户
    path('<int:owner_id>/links/', LinkListView.as_view(), name='links'),  # 友链
    path('comment/', CommentView.as_view(), name='comment'),  # 评论
]
