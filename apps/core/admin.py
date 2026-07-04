from django.contrib import admin
from solo.admin import SingletonModelAdmin

from .models import HeroStat, NavigationItem, SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(SingletonModelAdmin):
    """Одна запись — редактируется через `/admin/core/sitesettings/`."""

    fieldsets = (
        ('Логотип и баннер', {
            'fields': ('logo', 'banner'),
        }),
        ('Hero-баннер (тексты главной)', {
            'fields': (
                'hero_eyebrow',
                'hero_title', 'hero_title_accent',
                'hero_lead',
                'hero_primary_text',
                'hero_secondary_text', 'hero_secondary_url',
            ),
        }),
        ('CTA-блок «Присоединяйтесь»', {
            'fields': ('cta_title', 'cta_lead', 'cta_button_text'),
        }),
        ('Ссылка «Стать волонтёром» (одна на весь сайт)', {
            'fields': ('join_url',),
        }),
        ('Контакты', {
            'fields': (
                'email',
                'phone', 'phone_hint',
                'address', 'address_hint',
                'vk_url', 'telegram_url', 'youtube_url',
                'map_embed',
            ),
        }),
        ('Интеграция с ВКонтакте', {
            'fields': ('vk_group_id',),
            'description': 'Токен приложения хранится в переменной окружения VK_SERVICE_TOKEN.',
        }),
    )


@admin.register(NavigationItem)
class NavigationItemAdmin(admin.ModelAdmin):
    list_display = ('label', 'slug', 'url', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    ordering = ('order',)


@admin.register(HeroStat)
class HeroStatAdmin(admin.ModelAdmin):
    list_display = ('number', 'label', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('is_active',)
    ordering = ('order',)
