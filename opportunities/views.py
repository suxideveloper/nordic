from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from .models import Vacancy, VacancyCategory, Internship, Grant, GrantCategory


# ─── Vacancies ────────────────────────────────────────────────────────────────

def vacancy_list(request):
    vacancies = Vacancy.objects.filter(is_active=True).select_related('partner', 'category')
    category_slug = request.GET.get('category')
    emp_type = request.GET.get('type')
    search = request.GET.get('q', '')

    if category_slug:
        vacancies = vacancies.filter(category__slug=category_slug)
    if emp_type:
        vacancies = vacancies.filter(employment_type=emp_type)
    if search:
        vacancies = vacancies.filter(title__icontains=search) | vacancies.filter(short_description__icontains=search)

    # Pagination
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    paginator = Paginator(vacancies, 6)
    page = request.GET.get('page')
    try:
        paginated_vacancies = paginator.page(page)
    except PageNotAnInteger:
        paginated_vacancies = paginator.page(1)
    except EmptyPage:
        paginated_vacancies = paginator.page(paginator.num_pages)

    categories = VacancyCategory.objects.all()
    context = {
        'vacancies': paginated_vacancies,
        'categories': categories,
        'employment_choices': Vacancy.EMPLOYMENT_CHOICES,
        'selected_category': category_slug,
        'selected_type': emp_type,
        'search': search,
    }
    return render(request, 'opportunities/vacancy_list.html', context)


def vacancy_detail(request, slug):
    vacancy = get_object_or_404(Vacancy, slug=slug, is_active=True)
    vacancy.views_count += 1
    vacancy.save(update_fields=['views_count'])
    related = Vacancy.objects.filter(is_active=True, category=vacancy.category).exclude(pk=vacancy.pk)[:3]
    return render(request, 'opportunities/vacancy_detail.html', {'vacancy': vacancy, 'related': related})


# ─── Internships ──────────────────────────────────────────────────────────────

def internship_list(request):
    internships = Internship.objects.filter(is_active=True).select_related('partner')
    is_paid = request.GET.get('paid')
    search = request.GET.get('q', '')

    if is_paid == 'yes':
        internships = internships.filter(is_paid=True)
    elif is_paid == 'no':
        internships = internships.filter(is_paid=False)
    if search:
        internships = internships.filter(title__icontains=search) | internships.filter(short_description__icontains=search)

    # Pagination
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    paginator = Paginator(internships, 6)
    page = request.GET.get('page')
    try:
        paginated_internships = paginator.page(page)
    except PageNotAnInteger:
        paginated_internships = paginator.page(1)
    except EmptyPage:
        paginated_internships = paginator.page(paginator.num_pages)

    context = {
        'internships': paginated_internships,
        'search': search,
        'paid_filter': is_paid,
    }
    return render(request, 'opportunities/internship_list.html', context)


def internship_detail(request, slug):
    internship = get_object_or_404(Internship, slug=slug, is_active=True)
    internship.views_count += 1
    internship.save(update_fields=['views_count'])
    related = Internship.objects.filter(is_active=True).exclude(pk=internship.pk)[:3]
    return render(request, 'opportunities/internship_detail.html', {'internship': internship, 'related': related})


# ─── Grants ───────────────────────────────────────────────────────────────────

def grant_list(request):
    grants = Grant.objects.filter(is_active=True).select_related('partner', 'category')
    category_slug = request.GET.get('category')
    grant_type = request.GET.get('type')
    search = request.GET.get('q', '')

    if category_slug:
        grants = grants.filter(category__slug=category_slug)
    if grant_type:
        grants = grants.filter(grant_type=grant_type)
    if search:
        grants = grants.filter(title__icontains=search) | grants.filter(short_description__icontains=search)

    # Pagination
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    paginator = Paginator(grants, 6)
    page = request.GET.get('page')
    try:
        paginated_grants = paginator.page(page)
    except PageNotAnInteger:
        paginated_grants = paginator.page(1)
    except EmptyPage:
        paginated_grants = paginator.page(paginator.num_pages)

    categories = GrantCategory.objects.all()
    context = {
        'grants': paginated_grants,
        'categories': categories,
        'grant_types': Grant.GRANT_TYPE_CHOICES,
        'selected_category': category_slug,
        'selected_type': grant_type,
        'search': search,
    }
    return render(request, 'opportunities/grant_list.html', context)


def grant_detail(request, slug):
    grant = get_object_or_404(Grant, slug=slug, is_active=True)
    grant.views_count += 1
    grant.save(update_fields=['views_count'])
    related = Grant.objects.filter(is_active=True, category=grant.category).exclude(pk=grant.pk)[:3]
    return render(request, 'opportunities/grant_detail.html', {'grant': grant, 'related': related})
