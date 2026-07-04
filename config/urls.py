"""
URL-конфигурация ИРВЦ.

Имена маршрутов совпадают с active_page в шаблонах:
  home, team, news, projects, contacts, api-contact.
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path

from apps.core.views import HomeView
from apps.team.views import TeamView
from apps.news.views import NewsView
from apps.projects.views import ProjectsView
from apps.contacts.views import ContactsView, api_contact

urlpatterns = [
    path('admin/', admin.site.urls),

    path('',           HomeView.as_view(),     name='home'),
    path('team/',      TeamView.as_view(),     name='team'),
    path('news/',      NewsView.as_view(),     name='news'),
    path('projects/',  ProjectsView.as_view(), name='projects'),
    path('contacts/',  ContactsView.as_view(), name='contacts'),
    path('api/contact/', api_contact,          name='api-contact'),
]

# Раздача media/ в режиме разработки. В продакшене — Nginx.
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
