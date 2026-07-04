"""
Views приложения core: сейчас только главная страница.
"""
from django.views.generic import TemplateView

from apps.news.models import VkPost
from apps.team.models import TeamMember

from .models import HeroStat


class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx['hero_stats'] = HeroStat.objects.filter(is_active=True)
        ctx['news_preview'] = VkPost.objects.filter(is_visible=True)[:3]
        ctx['team_preview'] = TeamMember.objects.filter(is_active=True).select_related('group')[:4]
        return ctx
