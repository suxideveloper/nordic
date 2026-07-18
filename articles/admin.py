from django.contrib import admin
from .models import Article, Category, ArticleView


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon', 'color']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'difficulty', 'is_published', 'is_featured', 'view_count', 'published_at']
    list_filter = ['is_published', 'is_featured', 'difficulty', 'category']
    list_editable = ['is_published', 'is_featured']
    search_fields = ['title', 'excerpt', 'tags']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['view_count', 'created_at', 'updated_at', 'published_at']
    fieldsets = (
        ('Content', {
            'fields': ('title', 'slug', 'category', 'author', 'author_name', 'cover_image', 'excerpt', 'content')
        }),
        ('Metadata', {
            'fields': ('difficulty', 'read_time', 'tags')
        }),
        ('Publishing', {
            'fields': ('is_published', 'is_featured', 'published_at')
        }),
        ('Statistics', {
            'fields': ('view_count', 'created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(ArticleView)
class ArticleViewAdmin(admin.ModelAdmin):
    list_display = ['article', 'ip_address', 'session_key', 'viewed_at']
    list_filter = ['article', 'viewed_at']
    readonly_fields = ['article', 'ip_address', 'session_key', 'viewed_at']
    ordering = ['-viewed_at']
