from django.contrib import admin

from .models import TeamGroup, TeamMember


class TeamMemberInline(admin.TabularInline):
    model = TeamMember
    extra = 1
    fields = ('name', 'position', 'photo', 'order', 'is_active')


@admin.register(TeamGroup)
class TeamGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'order', 'members_count')
    list_editable = ('order',)
    ordering = ('order',)
    inlines = [TeamMemberInline]

    @admin.display(description='Кол-во участников')
    def members_count(self, obj):
        return obj.members.count()


@admin.register(TeamMember)
class TeamMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'position', 'group', 'order', 'is_active')
    list_editable = ('order', 'is_active')
    list_filter = ('group', 'is_active')
    search_fields = ('name', 'position')
    ordering = ('group__order', 'order')
