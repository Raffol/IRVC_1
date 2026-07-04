from django.contrib import admin

from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact', 'message_short', 'created_at', 'is_processed')
    list_filter = ('is_processed', 'created_at')
    list_editable = ('is_processed',)
    search_fields = ('name', 'contact', 'message')
    readonly_fields = ('name', 'contact', 'message', 'created_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)

    @admin.display(description='Сообщение')
    def message_short(self, obj):
        return obj.message[:60] + '…' if len(obj.message) > 60 else obj.message
