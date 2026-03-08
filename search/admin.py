"""
Admin configuration for search app.
"""
from django.contrib import admin
from .models import SearchQuery


@admin.register(SearchQuery)
class SearchQueryAdmin(admin.ModelAdmin):
    """Admin configuration for SearchQuery model."""
    
    list_display = ('query', 'results_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('query',)
    readonly_fields = ('created_at',)


