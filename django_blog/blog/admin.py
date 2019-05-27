from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html
from django.contrib.admin.models import LogEntry

from django_blog.custom_site import custom_site
from .models import (
    Post,
    Category,
    Tag,
)
from .admin_forms import PostAdminForm
from django_blog.base_admin import BaseOwnerAdmin


@admin.register(Category, site=custom_site)
class CategoryAdmin(BaseOwnerAdmin):
    form = PostAdminForm
    list_display = (
        'name',
        'status',
        'is_nav',
        'owner',
        'post_count',
        'created_time',
    )
    fields = (
        'name',
        'status',
        'is_nav',
    )

    def post_count(self, obj):
        return obj.post_set.count()

    post_count.short_description = '文章数量'


@admin.register(Tag, site=custom_site)
class TagAdmin(BaseOwnerAdmin):
    list_display = (
        'name',
        'status',
        'owner',
        'created_time',
    )
    fields = (
        'name',
        'status',
    )


class CategoryOwnerFilter(admin.SimpleListFilter):
    '''
    自定义过滤器, 只展示当前用户分类
    '''
    title = '分类过滤器'
    parameter_name = 'owner_category'

    def lookups(self, request, model_admin):
        return Category.objects.filter(owner=request.user).values_list('id', 'name')

    def queryset(self, request, queryset):
        category_id = self.value()
        if category_id:
            return queryset.filter(category_id=self.value())
        return queryset


@admin.register(Post, site=custom_site)
class PostAdmin(BaseOwnerAdmin):
    form = PostAdminForm
    list_display = [
        'title',
        'category',
        'status',
        'created_time',
        'owner',
        'operator',
    ]
    list_display_links = []

    list_filter = [CategoryOwnerFilter, ]
    search_fields = ['title', 'category__name']

    # 动作相关的配置在顶部和底部均显示
    actions_on_top = True
    actions_on_bottom = True

    fieldsets = (
        ('文章分类', {
            'description': '分类和标签',
            'fields': (
                ('category', 'tag'),
            ),
        }),
        ('内容', {
            'description': '文章内容',
            'fields': (
                'title',
                'desc',
                'content',
            ),
        }),
        ('文章状态', {
            'description': '正常、删除和草稿',
            'fields': (
                'status',
            ),
        }),
    )

    filter_horizontal = ('tag', )

    def operator(self, obj):
        return format_html(
            '<a href="{}">编辑</a>',
            reverse('cus_admin:blog_post_change', args=(obj.id, ))
        )
    operator.short_description = '操作'


@admin.register(LogEntry, site=custom_site)
class LogEntryAdmin(admin.ModelAdmin):
    list_display = [
        'object_repr',
        'object_id',
        'action_flag',
        'user',
        'change_message',
    ]
