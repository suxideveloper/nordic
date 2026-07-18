from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Event, EventCategory


def event_list(request):
    events = Event.objects.filter(is_published=True)
    category_slug = request.GET.get('category')
    format_filter = request.GET.get('format')
    search = request.GET.get('q', '')

    if category_slug:
        events = events.filter(category__slug=category_slug)
    if format_filter:
        events = events.filter(format=format_filter)
    if search:
        events = events.filter(title__icontains=search) | events.filter(short_description__icontains=search)

    upcoming = events.filter(start_date__gte=timezone.now()).order_by('start_date')
    past = events.filter(start_date__lt=timezone.now()).order_by('-start_date')
    categories = EventCategory.objects.all()

    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    
    paginator = Paginator(upcoming, 6)
    page = request.GET.get('page')
    try:
        paginated_upcoming = paginator.page(page)
    except PageNotAnInteger:
        paginated_upcoming = paginator.page(1)
    except EmptyPage:
        paginated_upcoming = paginator.page(paginator.num_pages)

    context = {
        'upcoming_events': paginated_upcoming,
        'past_events': past,
        'categories': categories,
        'selected_category': category_slug,
        'selected_format': format_filter,
        'search': search,
    }
    return render(request, 'events/event_list.html', context)


def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug, is_published=True)
    event.views_count += 1
    event.save(update_fields=['views_count'])

    related = Event.objects.filter(
        is_published=True, category=event.category
    ).exclude(pk=event.pk).order_by('-start_date')[:3]

    return render(request, 'events/event_detail.html', {
        'event': event,
        'related_events': related,
    })
