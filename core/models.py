from django.db import models


class Partner(models.Model):
    """Company or organization that posts vacancies/internships."""
    name = models.CharField(max_length=200)
    logo = models.ImageField(upload_to='partners/logos/', blank=True, null=True)
    website = models.URLField(blank=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class SiteSettings(models.Model):
    """Singleton model for site-wide settings."""
    university_name = models.CharField(max_length=200, default="Nordic University Tashkent")
    tagline = models.CharField(max_length=300, default="Your Gateway to Global Opportunities")
    logo = models.ImageField(upload_to='site/', blank=True, null=True)
    contact_email = models.EmailField(default="info@nordicuni.uz")
    contact_phone = models.CharField(max_length=50, default="+998 71 000 00 00")
    address = models.CharField(max_length=300, default="Tashkent, Uzbekistan")
    facebook = models.URLField(blank=True)
    instagram = models.URLField(blank=True)
    telegram = models.URLField(blank=True)
    linkedin = models.URLField(blank=True)

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return self.university_name

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
