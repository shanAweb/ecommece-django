"""
Models for search app.
"""
from django.db import models


class SearchQuery(models.Model):
    """Track search queries for analytics."""
    
    query = models.CharField(max_length=255)
    results_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'search_queries'
        verbose_name = 'Search Query'
        verbose_name_plural = 'Search Queries'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.query


