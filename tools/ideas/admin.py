from django.contrib import admin

from tools.ideas.models import Idea

class IdeaAdmin(admin.ModelAdmin):
    list_display = ('task', 'rating')
    ordering = ('-time',)
    raw_id_fields = ('task',)

admin.site.register(Idea, IdeaAdmin)
