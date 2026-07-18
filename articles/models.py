from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from ckeditor_uploader.fields import RichTextUploadingField


class Category(models.Model):
    """Article category."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True)
    icon = models.CharField(max_length=50, default='bi bi-folder', help_text="Bootstrap icon class, e.g. bi bi-briefcase")
    color = models.CharField(max_length=20, default='#6C63FF', help_text="HEX color for the category badge")
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Category"
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Article(models.Model):
    """Career guidance article for students."""
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]

    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True, blank=True, max_length=320)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='articles')
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    author_name = models.CharField(max_length=150, blank=True, help_text="Displayed author name (overrides user name)")

    cover_image = models.ImageField(upload_to='articles/covers/', blank=True, null=True)
    excerpt = models.TextField(max_length=400, blank=True, help_text="Short summary shown in article cards")
    content = RichTextUploadingField(config_name='default')

    difficulty = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    read_time = models.PositiveSmallIntegerField(default=1, help_text="Estimated reading time in minutes (auto-calculated)")
    tags = models.CharField(max_length=300, blank=True, help_text="Comma-separated tags, e.g. CV, Interview, LinkedIn")

    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False, help_text="Show on homepage / featured section")

    # View counting
    view_count = models.PositiveIntegerField(default=0, editable=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    published_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = "Article"
        verbose_name_plural = "Articles"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.title)
            slug = base
            counter = 1
            while Article.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{counter}"
                counter += 1
            self.slug = slug
        # Set published_at automatically when first published
        if self.is_published and not self.published_at:
            from django.utils import timezone
            self.published_at = timezone.now()

        # Calculate read_time automatically
        if self.content:
            from django.utils.html import strip_tags
            import math
            text = strip_tags(self.content)
            word_count = len(text.split())
            # Assume average reading speed is 200 words per minute
            self.read_time = max(1, math.ceil(word_count / 200.0))

        super().save(*args, **kwargs)

    def get_tag_list(self):
        """Returns tags as a list."""
        if self.tags:
            return [t.strip() for t in self.tags.split(',') if t.strip()]
        return []

    def get_author_display(self):
        """Returns the display name for the author."""
        if self.author_name:
            return self.author_name
        if self.author:
            return self.author.get_full_name() or self.author.username
        return "Nordic University"

    def get_difficulty_color(self):
        colors = {
            'beginner': '#00D4AA',
            'intermediate': '#FFD166',
            'advanced': '#FF6B35',
        }
        return colors.get(self.difficulty, '#6C63FF')


class ArticleView(models.Model):
    """Tracks unique article views per session/IP to prevent abuse."""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='views')
    ip_address = models.GenericIPAddressField()
    session_key = models.CharField(max_length=40, blank=True)
    viewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Each IP can only be counted once per article per day
        verbose_name = "Article View"
        verbose_name_plural = "Article Views"

    def __str__(self):
        return f"{self.article.title} — {self.ip_address}"
