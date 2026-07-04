from django.db.models import Prefetch
from django.views.generic import TemplateView

from .models import TeamGroup, TeamMember


class TeamView(TemplateView):
    template_name = 'team.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Загружаем группы + сразу их активных участников, чтобы не было N+1
        ctx['team_groups'] = TeamGroup.objects.prefetch_related(
            Prefetch(
                'members',
                queryset=TeamMember.objects.filter(is_active=True).order_by('order'),
            )
        )
        return ctx
