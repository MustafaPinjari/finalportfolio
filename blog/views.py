from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import BlogPost, Category, Comment
from .forms import CommentForm
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Comment
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import ContactMessage
from django.db.models import Sum
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from datetime import timedelta
from .models import PageView, UserActivity, BlogPost, Comment, Category

def blog_list(request):
    category_slug = request.GET.get('category')
    search_query = request.GET.get('q')
    tag_slug = request.GET.get('tag')
    
    posts = BlogPost.objects.all().order_by('-created_at')
    
    # Search functionality
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(tags__name__icontains=search_query)
        ).distinct()
    
    # Category filtering
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        posts = posts.filter(category=category)
    
    # Tag filtering
    if tag_slug:
        posts = posts.filter(tags__slug=tag_slug)
    
    # Pagination
    paginator = Paginator(posts, 6)  # 6 posts per page
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    # Get all categories and tags for sidebar
    categories = Category.objects.all()
    
    context = {
        'posts': posts,
        'categories': categories,
        'search_query': search_query,
    }
    
    return render(request, 'blog/blog_list.html', context)

def blog_detail(request, slug):
    post = get_object_or_404(BlogPost, slug=slug)
    comments = post.comments.filter(parent=None)
    
    if request.method == 'POST' and request.user.is_authenticated:
        parent_id = request.POST.get('parent_id')
        content = request.POST.get('content')
        
        if parent_id:
            parent_comment = Comment.objects.get(id=parent_id)
            Comment.objects.create(
                post=post,
                author=request.user,
                content=content,
                parent=parent_comment
            )
        else:
            Comment.objects.create(
                post=post,
                author=request.user,
                content=content
            )
        
        return JsonResponse({'status': 'success'})
    
    # Increment view count
    post.views_count += 1
    post.save()
    
    context = {
        'post': post,
        'comments': comments,
    }
    
    return render(request, 'blog/blog_detail.html', context)


def like_comment(request, comment_id):
    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)
        if request.user in comment.likes.all():
            comment.likes.remove(request.user)
            liked = False
        else:
            comment.likes.add(request.user)
            liked = True
        return JsonResponse({
            'likes_count': comment.likes.count(),
            'liked': liked
        })
    return JsonResponse({'error': 'Invalid request'}, status=400)


def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        ContactMessage.objects.create(
            name=name,
            email=email,
            message=message
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Message sent successfully!'
        })
    
    return JsonResponse({
        'success': False,
        'message': 'Invalid request method'
    }, status=400)
    
    return redirect('home')


# Add this new view for handling favorites
@login_required
@csrf_exempt  # We're handling CSRF in our JS
@require_POST
def toggle_favorite(request, post_id):
    post = get_object_or_404(BlogPost, id=post_id)
    user_profile = request.user.profile
    
    # Toggle favorite status
    if post in user_profile.favorite_posts.all():
        user_profile.favorite_posts.remove(post)
        is_favorite = False
    else:
        user_profile.favorite_posts.add(post)
        is_favorite = True
    
    # Return JSON response for AJAX requests
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'is_favorite': is_favorite,
            'favorites_count': post.favorited_by.count(),
            'message': 'Post has been {} to favorites'.format('removed from' if not is_favorite else 'added')
        })
    
    # For non-AJAX requests, redirect back to the post
    return redirect('blog:blog_detail', slug=post.slug)


def get_analytics_data(request):
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # Post views over time
    post_views = PageView.objects.filter(
        timestamp__range=(start_date, end_date),
        path__startswith='/blog/'
    ).annotate(
        date=TruncDate('timestamp')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # User registrations
    user_registrations = UserActivity.objects.filter(
        action_type='register',
        timestamp__range=(start_date, end_date)
    ).annotate(
        date=TruncDate('timestamp')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Comment activity
    comment_activity = Comment.objects.filter(
        created_at__range=(start_date, end_date)
    ).annotate(
        date=TruncDate('created_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Category popularity
    category_stats = Category.objects.annotate(
        post_count=Count('posts'),
        view_count=Count('posts__views_count')
    ).values('name', 'post_count', 'view_count')
    
    return JsonResponse({
        'post_views': list(post_views),
        'user_registrations': list(user_registrations),
        'comment_activity': list(comment_activity),
        'category_stats': list(category_stats)
    })


def admin_analytics(request):
    if not request.user.is_staff:
        return redirect('login')
        
    context = {
        'active_tab': 'analytics',
        'title': 'Analytics Dashboard',
    }
    return render(request, 'admin/admin_analytics.html', context)


@login_required
def admin_blog(request):
    """Admin dashboard for blog management"""
    # Ensure user is staff
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
        
    # Get blog statistics
    total_posts = BlogPost.objects.count()
    total_comments = Comment.objects.count()
    total_categories = Category.objects.count()
    recent_posts = BlogPost.objects.order_by('-created_at')[:5]
    recent_comments = Comment.objects.order_by('-created_at')[:5]
    
    # Get popular posts - using the built-in views_count field
    popular_posts = BlogPost.objects.order_by('-views_count')[:5]
    
    context = {
        'active_tab': 'blog',
        'total_posts': total_posts,
        'total_comments': total_comments,
        'total_categories': total_categories,
        'recent_posts': recent_posts,
        'recent_comments': recent_comments,
        'popular_posts': popular_posts,
    }
    
    return render(request, 'admin/blog/dashboard.html', context)


def projects(request):
    """View for displaying all projects"""
    from .models import Project
    
    # Get all projects, with featured projects first
    projects_list = Project.objects.all().order_by('-featured', '-created_at')
    
    # Get categories for filtering
    categories = Category.objects.all()
    
    # Handle category filtering
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        projects_list = projects_list.filter(category=category)
    
    context = {
        'projects': projects_list,
        'categories': categories,
        'selected_category': category_slug
    }
    
    return render(request, 'blog/projects.html', context)
