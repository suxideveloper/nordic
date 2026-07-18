from django.db import models
from ckeditor.fields import RichTextField
from core.models import Partner


class EventCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, default='bi-calendar-event', help_text='Bootstrap icon class')
    color = models.CharField(max_length=20, default='#6C63FF')

    class Meta:
        verbose_name_plural = 'Event Categories'

    def __str__(self):
        return self.name


class Event(models.Model):
    FORMAT_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('hybrid', 'Hybrid'),
    ]

    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(EventCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name='events')
    organizer = models.ForeignKey(Partner, on_delete=models.SET_NULL, null=True, blank=True, related_name='events',
                                  help_text='Leave blank if organized by Nordic University')
    short_description = models.CharField(max_length=300)
    description = RichTextField()
    cover_image = models.ImageField(upload_to='events/covers/', blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True, null=True)
    location = models.CharField(max_length=300, blank=True)
    format = models.CharField(max_length=10, choices=FORMAT_CHOICES, default='offline')
    registration_url = models.URLField(blank=True, help_text='External registration link')
    seats_available = models.PositiveIntegerField(blank=True, null=True)
    is_free = models.BooleanField(default=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tags = models.CharField(max_length=300, blank=True, help_text='Comma-separated tags')
    is_published = models.BooleanField(default=False)
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.title

    def get_tags_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]
