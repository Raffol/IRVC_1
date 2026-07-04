from django.contrib import admin

from .models import Project, ProjectCategory


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'order')
    list_editable = ('order',)
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('order',)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'status', 'order', 'is_active')
    list_editable = ('status', 'order', 'is_active')
    list_filter = ('status', 'category', 'is_active')
    search_fields = ('title', 'lead')
    ordering = ('order',)
    fieldsets = (
        ('Основное', {
            'fields': ('title', 'category', 'status', 'lead'),
        }),
        ('Показатели на карточке', {
            'fields': (('stat_1_num', 'stat_1_label'),
                       ('stat_2_num', 'stat_2_label'),
                       ('stat_3_num', 'stat_3_label')),
            'description': 'Оставьте пустыми, чтобы скрыть показатель.',
        }),
        ('Отображение', {
            'fields': ('order', 'is_active'),
        }),
    )
