"""
Context processor для наших шаблонов.

Подключается в settings.TEMPLATES['OPTIONS']['context_processors'].
После этого в любом шаблоне доступны:
  - settings   — объект SiteSettings (даже если запись ещё не создана — get_solo() её создаст)
  - nav_items  — активные пункты навигации в порядке order
  - active_page — идентификатор текущей страницы (для подсветки пункта меню)
"""
from .models import NavigationItem, SiteSettings


def site_context(request):
    active_page = getattr(request, 'resolver_match', None)
    active_page = active_page.url_name if active_page else None

    return {
        'settings': SiteSettings.get_solo(),
        'nav_items': list(NavigationItem.objects.filter(is_active=True)),
        'active_page': active_page,
    }
