from django.db import models
from ckeditor.fields import RichTextField
from core.models import Partner


# ─── Shared base ─────────────────────────────────────────────────────────────

class BaseOpportunity(models.Model):
    """Abstract base for Vacancy, Internship, Grant."""
    title = models.CharField(max_length=300)
    slug = models.SlugField(unique=True)
    partner = models.ForeignKey(Partner, on_delete=models.CASCADE, related_name='%(class)ss')
    short_description = models.CharField(max_length=300)
    description = RichTextField()
    cover_image = models.ImageField(upload_to='opportunities/', blank=True, null=True)
    apply_url = models.URLField(blank=True, help_text='External application link')
    deadline = models.DateField(blank=True, null=True)
    tags = models.CharField(max_length=300, blank=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    views_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def get_tags_list(self):
        return [t.strip() for t in self.tags.split(',') if t.strip()]


# ─── Vacancy ──────────────────────────────────────────────────────────────────

class VacancyCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, default='bi-briefcase')

    class Meta:
        verbose_name_plural = 'Vacancy Categories'

    def __str__(self):
        return self.name


class Vacancy(BaseOpportunity):
    EMPLOYMENT_CHOICES = [
        ('full_time', 'Full-time'),
        ('part_time', 'Part-time'),
        ('remote', 'Remote'),
        ('contract', 'Contract'),
    ]

    category = models.ForeignKey(VacancyCategory, on_delete=models.SET_NULL, null=True, blank=True)
    employment_type = models.CharField(max_length=20, choices=EMPLOYMENT_CHOICES, default='full_time')
    location = models.CharField(max_length=200, blank=True)
    salary_min = models.PositiveIntegerField(blank=True, null=True)
    salary_max = models.PositiveIntegerField(blank=True, null=True)
    salary_currency = models.CharField(max_length=10, default='USD')
    requirements = models.TextField(blank=True)
    is_for_students = models.BooleanField(default=False, help_text='Suitable for current students')

    class Meta:
        verbose_name_plural = 'Vacancies'
        ordering = ['-created_at']

    def salary_display(self):
        if self.salary_min and self.salary_max:
            return f"{self.salary_min:,} – {self.salary_max:,} {self.salary_currency}"
        elif self.salary_min:
            return f"From {self.salary_min:,} {self.salary_currency}"
        return "Negotiable"


# ─── Internship ───────────────────────────────────────────────────────────────

class Internship(BaseOpportunity):
    DURATION_CHOICES = [
        ('1_month', '1 Month'),
        ('2_months', '2 Months'),
        ('3_months', '3 Months'),
        ('6_months', '6 Months'),
        ('1_year', '1 Year'),
        ('flexible', 'Flexible'),
    ]

    location = models.CharField(max_length=200, blank=True)
    duration = models.CharField(max_length=20, choices=DURATION_CHOICES, default='3_months')
    is_paid = models.BooleanField(default=False)
    stipend = models.PositiveIntegerField(blank=True, null=True)
    stipend_currency = models.CharField(max_length=10, default='USD')
    field_of_study = models.CharField(max_length=200, blank=True, help_text='Relevant fields of study')
    start_date = models.DateField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def stipend_display(self):
        if self.is_paid and self.stipend:
            return f"{self.stipend:,} {self.stipend_currency}/month"
        return "Unpaid / Volunteer"


# ─── Grant ────────────────────────────────────────────────────────────────────

class GrantCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=50, default='bi-award')

    class Meta:
        verbose_name_plural = 'Grant Categories'

    def __str__(self):
        return self.name


class Grant(BaseOpportunity):
    GRANT_TYPE_CHOICES = [
        ('scholarship', 'Scholarship'),
        ('research', 'Research Grant'),
        ('travel', 'Travel Grant'),
        ('startup', 'Startup Grant'),
        ('other', 'Other'),
    ]

    category = models.ForeignKey(GrantCategory, on_delete=models.SET_NULL, null=True, blank=True)
    grant_type = models.CharField(max_length=20, choices=GRANT_TYPE_CHOICES, default='scholarship')
    amount = models.PositiveIntegerField(blank=True, null=True, help_text='Grant amount in USD')
    currency = models.CharField(max_length=10, default='USD')
    eligibility = models.TextField(blank=True, help_text='Who can apply?')
    country = models.CharField(max_length=100, blank=True, help_text='Country of opportunity')
    is_fully_funded = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def amount_display(self):
        if self.is_fully_funded:
            return "Fully Funded"
        if self.amount:
            return f"Up to {self.amount:,} {self.currency}"
        return "Varies"
