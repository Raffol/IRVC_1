from django.views.generic import ListView

from .models import VkPost


class NewsView(ListView):
    model = VkPost
    template_name = 'news.html'
    context_object_name = 'posts'
    paginate_by = 9

    def get_queryset(self):
        return VkPost.objects.filter(is_visible=True)
