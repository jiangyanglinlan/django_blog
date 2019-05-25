from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import (
    Post,
    Category,
    Tag,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
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

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(CategoryAdmin, self).save_model(request, obj, form, change)

    def post_count(self, obj):
        return obj.post_set.count()

    post_count.short_description = '文章数量'


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
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

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(TagAdmin, self).save_model(request, obj, form, change)


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


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
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

    # 隐藏 owner
    exclude = ('owner', )

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
            reverse('admin:blog_post_change', args=(obj.id, ))
        )

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(PostAdmin, self).save_model(request, obj, form, change)

    def get_queryset(self, request):
        qs = super(PostAdmin, self).get_queryset(request)
        return qs.filter(owner=request.user)
