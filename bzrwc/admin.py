from django.contrib import admin

from bzrwc import models

class ChartInline(admin.TabularInline):
    model = models.Chart
    extra = 1

class RepositoryAdmin(admin.ModelAdmin):
    inlines = [ChartInline]
    list_display = ('name', 'owner', 'slug', 'url')
    list_filter = ('owner',)
    ordering = ('owner', 'name',)
    prepopulated_fields = {
        'slug': ('name',)
    }

class ChartAdmin(admin.ModelAdmin):
    list_display = ('repository', 'name', 'filter', 'exclude')
    list_filter = ('repository',)
    ordering = ('repository', 'name')
    prepopulated_fields = {
        'slug': ('name',)
    }

class RevisionAdmin(admin.ModelAdmin):
    list_display = ('chart', 'revision_no',
        'num_lines', 'num_words', 'num_chars', 'num_bytes')
    list_filter = ('chart',)
    ordering = ('chart', 'timestamp')

admin.site.register(models.Repository, RepositoryAdmin)
admin.site.register(models.Chart, ChartAdmin)
admin.site.register(models.Revision, RevisionAdmin)
