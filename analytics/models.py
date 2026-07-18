from django.db import models
from django.utils import timezone


class PageVisit(models.Model):
    """Tracks each page visit with time spent information."""
    path = models.CharField(max_length=500, db_index=True)
    page_name = models.CharField(max_length=200, blank=True)
    session_key = models.CharField(max_length=40, blank=True, db_index=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    referrer = models.URLField(max_length=500, blank=True)
    time_spent = models.PositiveIntegerField(default=0, help_text="Seconds spent on page")
    visited_at = models.DateTimeField(default=timezone.now, db_index=True)
    left_at = models.DateTimeField(null=True, blank=True)
    is_bot = models.BooleanField(default=False)

    class Meta:
        ordering = ['-visited_at']
        verbose_name = "Page Visit"
        verbose_name_plural = "Page Visits"
        indexes = [
            models.Index(fields=['path', 'visited_at']),
            models.Index(fields=['visited_at']),
        ]

    def __str__(self):
        return f"{self.path} — {self.visited_at.strftime('%Y-%m-%d %H:%M')}"

    @property
    def time_spent_display(self):
        """Human-readable time spent."""
        s = self.time_spent
        if s < 60:
            return f"{s}s"
        m, s = divmod(s, 60)
        if m < 60:
            return f"{m}m {s}s"
        h, m = divmod(m, 60)
        return f"{h}h {m}m"

    @classmethod
    def get_friendly_name(cls, path):
        """Convert URL path to friendly page name."""
        mapping = {
            '/': 'Home Page',
            '/events/': 'Events',
            '/opportunities/vacancies/': 'Vacancies',
            '/opportunities/internships/': 'Internships',
            '/opportunities/grants/': 'Grants',
            '/articles/': 'Articles',
            '/articles/career/': 'Career Articles',
        }
        if path in mapping:
            return mapping[path]
        # Dynamic paths
        if path.startswith('/events/'):
            return 'Event Detail'
        if path.startswith('/opportunities/vacancies/'):
            return 'Vacancy Detail'
        if path.startswith('/opportunities/internships/'):
            return 'Internship Detail'
        if path.startswith('/opportunities/grants/'):
            return 'Grant Detail'
        if path.startswith('/articles/'):
            return 'Article Detail'
        if path.startswith('/admin/'):
            return 'Admin Panel'
        return path
