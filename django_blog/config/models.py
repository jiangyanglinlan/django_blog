from django.contrib.auth.models import User
from django.db import models
from django.template.loader import render_to_string


class Link(models.Model):
    STATUS_NORMAL = 1
    STATUS_DELETE = 0
    STATUS_ITEMS = (
        (STATUS_NORMAL, '正常'),
        (STATUS_DELETE, '删除'),
    )
    title = models.CharField(max_length=50, verbose_name='标题')
    href = models.URLField(verbose_name='链接')
    status = models.PositiveIntegerField(default=STATUS_NORMAL,
                                         choices=STATUS_ITEMS, verbose_name='状态')
    weight = models.PositiveIntegerField(default=1, choices=zip(range(1, 6),
                                         range(1, 6)), verbose_name='权重',
                                         help_text='权重高展示顺序靠前')
    owner = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = verbose_name_plural = '友链'

    def __str__(self):
        return self.title


class SideBar(models.Model):
    DISPLAY_HTML = 1
    DISPLAY_LASTEST = 2
    DISPLAY_HOT = 3
    DISPLAY_COMMENT = 4

    STATUS_SHOW = 1
    STATUS_HIDE = 0
    STATUS_ITEMS = (
        (STATUS_SHOW, '展示'),
        (STATUS_HIDE, '隐藏'),
    )
    SIDE_TYPE = (
        (DISPLAY_HTML, 'HTML'),
        (DISPLAY_LASTEST, '最新文章'),
        (DISPLAY_HOT, '最热文章'),
        (DISPLAY_COMMENT, '最近评论'),
    )
    title = models.CharField(max_length=50, verbose_name='标题')
    display_type = models.PositiveIntegerField(default=1, choices=SIDE_TYPE,
                                               verbose_name='展示类型')
    content = models.CharField(max_length=500, blank=True, verbose_name='内容',
                               help_text='如果设置的不是 HTML 类型, 可为空')
    status = models.PositiveIntegerField(default=STATUS_SHOW, choices=STATUS_ITEMS,
                                         verbose_name='状态')
    owner = models.ForeignKey(User, verbose_name='作者', on_delete=models.CASCADE)
    created_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')

    class Meta:
        verbose_name = verbose_name_plural = '侧边栏'

    def __str__(self):
        return self.title

    @classmethod
    def get_all(cls):
        return cls.objects.filter(status=cls.STATUS_SHOW)

    @staticmethod
    def template_to_string(template, context):
        #  封装 render_to_tring 方法
        render_string = render_to_string(template, context=context)
        return render_string

    @property
    def content_html(self):
        # 直接渲染模板
        from blog.models import Post  # 避免循环引用
        from comment.models import Comment

        post_template = 'config/blocks/sidebar_posts.html'  # post template 路径
        comment_template = 'config/blocks/sidebar_comments.html'  # comment template 路径
        # 不同的 display_type 对应的 template
        templates = {
            self.DISPLAY_LASTEST: post_template,
            self.DISPLAY_HOT: post_template,
            self.DISPLAY_COMMENT: comment_template,
        }

        # 不同的 display_type 对应的 context
        display_type_contexts = {
            self.DISPLAY_LASTEST: {
                'posts': Post.lastest_posts(),
            },
            self.DISPLAY_HOT: {
                'posts': Post.hot_posts(),
            },
            self.DISPLAY_COMMENT: {
                'comments': Comment.objects.filter(status=Comment.STATUS_NORMAL),
            },
        }

        _template_to_string = self.template_to_string
        # 不同的 display_type 对应的 content_html
        contents_dict = {
            self.DISPLAY_HTML: self.content,
            self.DISPLAY_LASTEST: _template_to_string(templates[self.DISPLAY_LASTEST], display_type_contexts[self.DISPLAY_LASTEST]),
            self.DISPLAY_HOT: _template_to_string(templates[self.DISPLAY_HOT], display_type_contexts[self.DISPLAY_HOT]),
            self.DISPLAY_COMMENT: _template_to_string(templates[self.DISPLAY_COMMENT], display_type_contexts[self.DISPLAY_COMMENT]),
        }

        display_type = self.display_type  # 当前的 display_type
        content = contents_dict[display_type]
        return content