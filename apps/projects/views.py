import json

from django.views.generic import TemplateView

from .models import Project, ProjectCategory


class ProjectsView(TemplateView):
    template_name = 'projects.html'

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)

        projects = Project.objects.filter(is_active=True).select_related('category')
        categories = ProjectCategory.objects.all()

        # Для noscript-fallback
        ctx['projects'] = projects

        # JSON для Vue-острова. ensure_ascii=False — чтобы кириллица шла как есть,
        # Django-шаблон сам экранирует кавычки внутри атрибута.
        ctx['project_categories_json'] = json.dumps(
            [{'slug': c.slug, 'name': c.name} for c in categories],
            ensure_ascii=False,
        )
        ctx['projects_json'] = json.dumps(
            [
                {
                    'id': p.id,
                    'title': p.title,
                    'lead': p.lead,
                    'status': p.status,
                    'category_slug': p.category.slug,
                    'stats': p.get_stats(),
                }
                for p in projects
            ],
            ensure_ascii=False,
        )
        return ctx
