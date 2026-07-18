from django.shortcuts import render
from events.models import Event
from opportunities.models import Vacancy, Internship, Grant
from core.models import Partner


from articles.models import Article

def home(request):
    """Homepage - shows featured content from all sections."""
    context = {
        'featured_events': Event.objects.filter(is_published=True).order_by('-start_date')[:4],
        'featured_vacancies': Vacancy.objects.filter(is_active=True).order_by('-created_at')[:3],
        'featured_internships': Internship.objects.filter(is_active=True).order_by('-created_at')[:3],
        'featured_grants': Grant.objects.filter(is_active=True).order_by('-deadline')[:3],
        'partners': Partner.objects.filter(is_active=True)[:8],

        # Real statistics counts
        'events_count': Event.objects.filter(is_published=True).count(),
        'vacancies_count': Vacancy.objects.filter(is_active=True).count(),
        'internships_count': Internship.objects.filter(is_active=True).count(),
        'grants_count': Grant.objects.filter(is_active=True).count(),
        'partners_count': Partner.objects.filter(is_active=True).count(),
        'articles_count': Article.objects.filter(is_published=True).count(),

        # Featured/latest articles for the homepage reference
        'latest_articles': Article.objects.filter(is_published=True).order_by('-published_at', '-created_at')[:3],
    }
    return render(request, 'core/home.html', context)


def about(request):
    from django.urls import reverse
    from django.contrib.auth.models import User
    
    students_count = User.objects.filter(is_active=True).count()
    partners_count = Partner.objects.filter(is_active=True).count()
    events_count = Event.objects.filter(is_published=True).count()
    vacancies_count = Vacancy.objects.filter(is_active=True).count()
    articles_count = Article.objects.filter(is_published=True).count()
    grants_count = Grant.objects.filter(is_active=True).count()
    
    offerings = [
        ('bi bi-calendar-event-fill', '#6C63FF', 'Events', 'Conferences, workshops, hackathons organized by Nordic and our partners.', reverse('events:list')),
        ('bi bi-briefcase-fill', '#00D4AA', 'Vacancies', 'Full-time, part-time and remote job openings from industry leaders.', reverse('opportunities:vacancy_list')),
        ('bi bi-laptop', '#FF6B35', 'Internships', 'Paid and unpaid internships to gain hands-on real-world experience.', reverse('opportunities:internship_list')),
        ('bi bi-award-fill', '#FFD166', 'Grants', 'Scholarships, research grants and international funding opportunities.', reverse('opportunities:grant_list')),
    ]
    
    context = {
        'offerings': offerings,
        'students_count': students_count,
        'partners_count': partners_count,
        'events_count': events_count,
        'vacancies_count': vacancies_count,
        'articles_count': articles_count,
        'grants_count': grants_count,
    }
    return render(request, 'core/about.html', context)


def partners_list(request):
    partners_qs = Partner.objects.filter(is_active=True)
    
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    paginator = Paginator(partners_qs, 6)
    page = request.GET.get('page')
    try:
        paginated_partners = paginator.page(page)
    except PageNotAnInteger:
        paginated_partners = paginator.page(1)
    except EmptyPage:
        paginated_partners = paginator.page(paginator.num_pages)
        
    return render(request, 'core/partners.html', {'partners': paginated_partners})
