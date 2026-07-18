from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Article, Category, ArticleView


def get_client_ip(request):
    """Extract the real client IP address from request."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '0.0.0.0')


def record_article_view(request, article):
    """
    Count a view only once per unique IP per article (per day logic).
    Atomically increments view_count on the Article.
    """
    ip = get_client_ip(request)
    session_key = request.session.session_key or ''

    # Ensure the session is created (needed for anonymous users)
    if not session_key:
        request.session.create()
        session_key = request.session.session_key or ''

    already_viewed = ArticleView.objects.filter(
        article=article,
        ip_address=ip,
    ).exists()

    if not already_viewed:
        ArticleView.objects.create(
            article=article,
            ip_address=ip,
            session_key=session_key,
        )
        # Use F() to avoid race conditions
        from django.db.models import F
        Article.objects.filter(pk=article.pk).update(view_count=F('view_count') + 1)
        # Refresh local instance
        article.refresh_from_db(fields=['view_count'])


def article_list(request):
    """List all published articles with optional category and search filter."""
    articles = Article.objects.filter(is_published=True).select_related('category', 'author')
    categories = Category.objects.all()

    # Filter by category
    category_slug = request.GET.get('category', '')
    if category_slug:
        articles = articles.filter(category__slug=category_slug)

    # Search
    q = request.GET.get('q', '').strip()
    if q:
        articles = articles.filter(
            Q(title__icontains=q) |
            Q(excerpt__icontains=q) |
            Q(tags__icontains=q)
        )

    # Filter by difficulty
    difficulty = request.GET.get('difficulty', '')
    if difficulty:
        articles = articles.filter(difficulty=difficulty)

    # Pagination
    from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
    
    paginator = Paginator(articles, 6)  # 6 articles per page
    page = request.GET.get('page')
    try:
        paginated_articles = paginator.page(page)
    except PageNotAnInteger:
        paginated_articles = paginator.page(1)
    except EmptyPage:
        paginated_articles = paginator.page(paginator.num_pages)

    featured = Article.objects.filter(is_published=True, is_featured=True).select_related('category')[:3]

    context = {
        'articles': paginated_articles,
        'categories': categories,
        'featured': featured,
        'selected_category': category_slug,
        'search_query': q,
        'selected_difficulty': difficulty,
        'total_count': articles.count(),
    }
    return render(request, 'articles/article_list.html', context)


def article_detail(request, slug):
    """Show a single article and record the view."""
    article = get_object_or_404(Article, slug=slug, is_published=True)

    # Record view (unique per IP)
    record_article_view(request, article)

    # Related articles (same category, excluding current)
    related = Article.objects.filter(
        is_published=True,
        category=article.category
    ).exclude(pk=article.pk).order_by('-view_count')[:4]

    context = {
        'article': article,
        'related': related,
        'tag_list': article.get_tag_list(),
    }
    return render(request, 'articles/article_detail.html', context)
