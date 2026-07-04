from django.contrib import admin

from .models import VkPost


@admin.register(VkPost)
class VkPostAdmin(admin.ModelAdmin):
    list_display = ('title_short', 'published_at', 'likes', 'comments', 'is_visible')
    list_editable = ('is_visible',)
    list_filter = ('is_visible', 'published_at')
    search_fields = ('title', 'text')
    ordering = ('-published_at',)
    readonly_fields = ('vk_id', 'url', 'published_at', 'likes', 'comments')

    fieldsets = (
        ('Отображение', {
            'fields': ('is_visible', 'title', 'text', 'image'),
        }),
        ('Автоматически из ВК (только чтение)', {
            'fields': ('vk_id', 'url', 'published_at', 'likes', 'comments'),
        }),
    )

    @admin.display(description='Заголовок')
    def title_short(self, obj):
        return obj.title or (obj.text[:60] + '…' if len(obj.text) > 60 else obj.text) or '—'
