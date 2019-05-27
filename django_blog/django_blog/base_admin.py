from django.contrib import admin


class BaseOwnerAdmin(admin.ModelAdmin):
    '''
    用来自动补充文章, 分类, 标签, 侧边栏, 友链这些 model 的 owner 字段
    针对 queryset 过滤当前用户的数据
    '''
    exclude = ['owner', ]

    def get_queryset(self, request):
        qs = super(BaseOwnerAdmin, self).get_queryset(request)
        return qs.filter(owner=request.user)

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(BaseOwnerAdmin, self).save_model(request, obj, form, change)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        qs = self.queryset_property(db_field, request)
        if qs is not None:
            kwargs['queryset'] = qs
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        qs = self.queryset_property(db_field, request)
        if qs is not None:
            kwargs['queryset'] = qs
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    @staticmethod
    def queryset_property(db_field, request):
        obj = db_field.remote_field.model
        fields = obj._meta.fields
        field_names = [field.name for field in fields]
        if 'owner' in field_names:
            return obj.objects.filter(owner=request.user)
        return None
