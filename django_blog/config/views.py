from django.views.generic import ListView


from blog.views import CommonViewMixin
from .models import Link


class LinkListView(CommonViewMixin, ListView):
    template_name = 'config/links.html'

    def get_queryset(self):
        # 重写 queryset, 根据分类过滤
        owner_id = self.kwargs.get('owner_id')
        queryset = Link.objects.filter(status=Link.STATUS_NORMAL).filter(owner__id=owner_id)
        return queryset
