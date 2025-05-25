from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib import messages
from blog.models import BlogPost, Comment, Category
from django.http import JsonResponse
from django.utils import timezone
import os
from datetime import timedelta
from .forms import UserEditForm, UserProfileForm, UserCreateForm, BlogPostForm, CategoryForm
from blog.models import PageView

# Helper function to check if user is admin or staff
def is_admin_or_staff(user):
    return user.is_superuser or user.is_staff

@login_required
@user_passes_test(is_admin_or_staff)
def custom_admin(request):
    """Admin dashboard view with overview of site statistics"""
    # Get statistics
    stats = {
        'user_count': User.objects.count(),
        'post_count': BlogPost.objects.count(),
        'comment_count': Comment.objects.count(),
    }

    # Get analytics data for the last 30 days
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)

    # Get page views trend
    page_views = PageView.objects.filter(
        timestamp__range=(start_date, end_date)
    ).values('timestamp__date').annotate(
        count=Count('id')
    ).order_by('timestamp__date')

    # Get user registrations trend
    user_registrations = User.objects.filter(
        date_joined__range=(start_date, end_date)
    ).values('date_joined__date').annotate(
        count=Count('id')
    ).order_by('date_joined__date')

    # Get comment activity trend
    comment_activity = Comment.objects.filter(
        created_at__range=(start_date, end_date)
    ).values('created_at__date').annotate(
        count=Count('id')
    ).order_by('created_at__date')

    # Get recent activities (newest users, posts, comments)
    recent_users = User.objects.order_by('-date_joined')[:5]
    recent_posts = BlogPost.objects.order_by('-created_at')[:5]
    recent_comments = Comment.objects.order_by('-created_at')[:5]

    # Combine all activities and sort by date
    recent_activities = []
    
    for user in recent_users:
        recent_activities.append({
            'type': 'user',
            'title': f'New user: {user.username}',
            'description': f'{user.first_name} {user.last_name}' if user.first_name else f'User {user.username}',
            'date': user.date_joined
        })
    
    for post in recent_posts:
        recent_activities.append({
            'type': 'post',
            'title': f'New post: {post.title}',
            'description': f'Published by {post.author.username}',
            'date': post.created_at
        })
    
    for comment in recent_comments:
        recent_activities.append({
            'type': 'comment',
            'title': f'New comment on "{comment.post.title}"',
            'description': f'By {comment.author.username}: {comment.content[:50]}{"..." if len(comment.content) > 50 else ""}',
            'date': comment.created_at
        })
    
    # Sort by date, newest first
    recent_activities = sorted(recent_activities, key=lambda x: x['date'], reverse=True)[:10]

    context = {
        'active_tab': 'dashboard',
        'stats': stats,
        'recent_activities': recent_activities,
        'analytics': {
            'page_views': list(page_views),
            'user_registrations': list(user_registrations),
            'comment_activity': list(comment_activity)
        }
    }
    
    return render(request, 'admin/custom_admin.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def admin_users(request):
    """Admin view for managing users"""
    # Get search and filter parameters
    search_query = request.GET.get('search', '')
    filter_param = request.GET.get('filter', '')
    
    # Filter users based on search and filter
    users = User.objects.all().order_by('-date_joined')
    
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) | 
            Q(email__icontains=search_query) |
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query)
        )
    
    if filter_param:
        if filter_param == 'staff':
            users = users.filter(is_staff=True)
        elif filter_param == 'superuser':
            users = users.filter(is_superuser=True)
        elif filter_param == 'active':
            users = users.filter(is_active=True)
        elif filter_param == 'inactive':
            users = users.filter(is_active=False)
    
    # Paginate users
    paginator = Paginator(users, 10)  # Show 10 users per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'active_tab': 'users',
        'users': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'paginator': paginator
    }
    
    return render(request, 'admin/admin_users.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def admin_user_create(request):
    """Admin view for creating a new user"""
    if request.method == 'POST':
        user_form = UserCreateForm(request.POST)
        if user_form.is_valid():
            user = user_form.save()
            messages.success(request, f'User {user.username} created successfully')
            return redirect('admin_users')
    else:
        user_form = UserCreateForm()
    
    context = {
        'active_tab': 'users',
        'user_form': user_form,
        'is_create': True
    }
    
    return render(request, 'admin/admin_user_form.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def admin_user_edit(request, user_id):
    """Admin view for editing an existing user"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user_form = UserEditForm(request.POST, instance=user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=user.profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, f'User {user.username} updated successfully')
            return redirect('admin_users')
    else:
        user_form = UserEditForm(instance=user)
        profile_form = UserProfileForm(instance=user.profile)
    
    context = {
        'active_tab': 'users',
        'user_form': user_form,
        'profile_form': profile_form,
        'user_obj': user,
        'is_create': False
    }
    
    return render(request, 'admin/admin_user_form.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def admin_user_toggle_active(request, user_id):
    """Toggle user active status"""
    if request.method == 'POST':
        user = get_object_or_404(User, id=user_id)
        
        # Don't allow deactivating yourself
        if user == request.user:
            messages.error(request, "You cannot deactivate your own account")
            return redirect('admin_users')
        
        user.is_active = not user.is_active
        user.save()
        
        status = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User {user.username} {status} successfully')
    
    return redirect('admin_users')

@login_required
@user_passes_test(is_admin_or_staff)
def admin_posts(request):
    """Admin view for managing blog posts"""
    # Get search and filter parameters
    search_query = request.GET.get('search', '')
    filter_param = request.GET.get('filter', '')
    
    # Filter posts based on search and filter
    posts = BlogPost.objects.all().order_by('-created_at')
    
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) | 
            Q(content__icontains=search_query) |
            Q(author__username__icontains=search_query)
        )
    
    if filter_param:
        if filter_param == 'published':
            posts = posts.filter(is_published=True)
        elif filter_param == 'draft':
            posts = posts.filter(is_published=False)
    
    # Paginate posts
    paginator = Paginator(posts, 10)  # Show 10 posts per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'active_tab': 'posts',
        'posts': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'paginator': paginator
    }
    
    return render(request, 'admin/admin_posts.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def admin_post_create(request):
    """Admin view for creating a new blog post"""
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            
            # Handle categories and tags
            form.save_m2m()  # Saves the many-to-many data for the form
            
            messages.success(request, 'Blog post created successfully!')
            return redirect('admin_posts')
    else:
        form = BlogPostForm()
    
    context = {
        'active_tab': 'posts',
        'form': form,
        'is_create': True,
        'form_title': 'Create New Post',
        'form_description': 'Add a new blog post to your site',
        'submit_text': 'Create Post'
    }
    
    return render(request, 'admin/admin_post_form.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def admin_post_edit(request, slug):
    """Admin view for editing a blog post"""
    post = get_object_or_404(BlogPost, slug=slug)
    
    if request.method == 'POST':
        form = BlogPostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'Blog post updated successfully!')
            return redirect('admin_posts')
    else:
        form = BlogPostForm(instance=post)
    
    context = {
        'active_tab': 'posts',
        'form': form,
        'post': post,
        'is_create': False,
        'form_title': f'Edit Post: {post.title}',
        'form_description': 'Update your blog post content and settings',
        'submit_text': 'Update Post'
    }
    
    return render(request, 'admin/admin_post_form.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def admin_post_toggle_published(request, slug):
    """Admin view for toggling post published status"""
    if request.method == 'POST':
        post = get_object_or_404(BlogPost, slug=slug)
        post.is_published = not post.is_published
        post.save()
        
        status = 'published' if post.is_published else 'unpublished'
        messages.success(request, f'Post "{post.title}" has been {status}.')
    
    return redirect('admin_posts')

@login_required
@user_passes_test(is_admin_or_staff)
def admin_post_delete(request, slug):
    """Admin view for deleting a blog post"""
    if request.method == 'POST':
        post = get_object_or_404(BlogPost, slug=slug)
        title = post.title
        post.delete()
        messages.success(request, f'Post "{title}" has been deleted.')
    
    return redirect('admin_posts')

@login_required
@user_passes_test(is_admin_or_staff)
def admin_comments(request):
    """Admin view for managing comments"""
    # Get search and filter parameters
    search_query = request.GET.get('search', '')
    filter_param = request.GET.get('filter', '')
    
    # Filter comments based on search and filter
    comments = Comment.objects.all().order_by('-created_at')
    
    if search_query:
        comments = comments.filter(
            Q(content__icontains=search_query) | 
            Q(author__username__icontains=search_query) |
            Q(post__title__icontains=search_query)
        )
    
    if filter_param:
        if filter_param == 'approved':
            comments = comments.filter(is_approved=True)
        elif filter_param == 'pending':
            comments = comments.filter(is_approved=False)
    
    # Paginate comments
    paginator = Paginator(comments, 15)  # Show 15 comments per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'active_tab': 'comments',
        'comments': page_obj,
        'page_obj': page_obj,
        'is_paginated': page_obj.has_other_pages(),
        'paginator': paginator
    }
    
    return render(request, 'admin/admin_comments.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def admin_comment_toggle_approved(request, comment_id):
    """Admin view for toggling comment approval status"""
    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)
        comment.is_approved = not comment.is_approved
        comment.save()
        
        status = 'approved' if comment.is_approved else 'unapproved'
        messages.success(request, f'Comment has been {status}.')
    
    return redirect('admin_comments')

@login_required
@user_passes_test(is_admin_or_staff)
def admin_comment_delete(request, comment_id):
    """Admin view for deleting a comment"""
    if request.method == 'POST':
        comment = get_object_or_404(Comment, id=comment_id)
        comment.delete()
        messages.success(request, 'Comment has been deleted.')
    
    return redirect('admin_comments')

@login_required
@user_passes_test(is_admin_or_staff)
def admin_categories(request):
    """Admin view for managing categories"""
    categories = Category.objects.annotate(post_count=Count('posts')).order_by('name')
    
    context = {
        'active_tab': 'categories',
        'categories': categories
    }
    
    return render(request, 'admin/admin_categories.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def admin_category_create(request):
    """Admin view for creating a new category"""
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully!')
            return redirect('admin_categories')
    else:
        form = CategoryForm()
    
    context = {
        'active_tab': 'categories',
        'form': form,
        'is_create': True,
        'form_title': 'Create New Category',
        'form_description': 'Add a new blog category',
        'submit_text': 'Create Category'
    }
    
    return render(request, 'admin/admin_category_form.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def admin_category_edit(request, slug):
    """Admin view for editing a category"""
    category = get_object_or_404(Category, slug=slug)
    
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category updated successfully!')
            return redirect('admin_categories')
    else:
        form = CategoryForm(instance=category)
    
    context = {
        'active_tab': 'categories',
        'form': form,
        'category': category,
        'is_create': False,
        'form_title': f'Edit Category: {category.name}',
        'form_description': 'Update your blog category details',
        'submit_text': 'Update Category'
    }
    
    return render(request, 'admin/admin_category_form.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def admin_category_delete(request, slug):
    """Admin view for deleting a category"""
    if request.method == 'POST':
        category = get_object_or_404(Category, slug=slug)
        # Only delete if there are no posts with this category
        if category.blogpost_set.count() == 0:
            name = category.name
            category.delete()
            messages.success(request, f'Category "{name}" has been deleted.')
        else:
            messages.error(request, 'Cannot delete a category that is assigned to posts.')
    
    return redirect('admin_categories')

@login_required
@user_passes_test(is_admin_or_staff)
def admin_media(request):
    """Admin view for managing media files"""
    # Logic for media management
    return render(request, 'admin/admin_media.html', {'active_tab': 'media'})

@login_required
@user_passes_test(is_admin_or_staff)
def admin_settings(request):
    """Admin view for site settings and backup management"""
    # Handle backup creation if requested
    backup_message = None
    restore_message = None
    
    # Import SEO models
    try:
        from seo.models import SeoMetadata, SeoScore, SeoIssue, Keyword, SitemapConfig
        from seo.forms import SitemapConfigForm
        from seo.utils import run_seo_analysis, generate_sitemap, ping_search_engines
        
        seo_app_missing = False
    except ImportError:
        seo_app_missing = True
    
    # Import backup models and forms
    try:
        from backup.models import BackupSchedule, BackupFile, RestorePoint
        from backup.forms import BackupScheduleForm, ManualBackupForm, RestoreForm, ImportForm
        from backup.utils import create_backup, restore_backup, import_backup
        
        # Handle manual backup creation
        if request.method == 'POST' and 'create_backup' in request.POST:
            try:
                # Get form data directly from POST
                note = request.POST.get('note', '')
                include_media = request.POST.get('include_media') == 'on'
                include_static = request.POST.get('include_static') == 'on'
                
                # Create backup record
                from django.utils import timezone
                timestamp = timezone.now().strftime('%Y%m%d_%H%M%S')
                
                backup = BackupFile(
                    filename=f"manual_backup_{timestamp}.zip",
                    backup_type='manual',
                    note=note
                )
                backup.save()
                
                # Create the backup
                success, result = create_backup(
                    backup,
                    include_media=include_media,
                    include_static=include_static
                )
                
                if success:
                    backup_message = {'type': 'success', 'text': f'Backup created successfully. Filename: manual_backup_{timestamp}.zip'}
                else:
                    backup_message = {'type': 'error', 'text': f'Error creating backup: {result}'}
            except Exception as e:
                backup_message = {'type': 'error', 'text': f'Exception during backup: {str(e)}'}
        else:
            backup_form = ManualBackupForm()
        
        # Handle backup import
        if request.method == 'POST' and 'import_backup' in request.POST:
            try:
                if 'backup_file' not in request.FILES:
                    backup_message = {'type': 'error', 'text': 'No backup file uploaded'}
                else:
                    backup_file = request.FILES['backup_file']
                    
                    # Process the import
                    success, result = import_backup(
                        backup_file, 
                        name=f'Imported {timezone.now().strftime("%Y-%m-%d %H:%M:%S")}',
                        note='Imported via admin panel'
                    )
                    
                    if success:
                        backup_message = {'type': 'success', 'text': 'Backup imported successfully.'}
                    else:
                        backup_message = {'type': 'error', 'text': f'Error importing backup: {result}'}
            except Exception as e:
                backup_message = {'type': 'error', 'text': f'Exception during import: {str(e)}'}
        
        # Handle restore point creation
        elif request.method == 'POST' and 'create_restore_point' in request.POST:
            try:
                # Get form data directly from POST
                name = request.POST.get('name', '')
                backup_id = request.POST.get('backup', '')
                note = request.POST.get('note', '')
                
                if not name or not backup_id:
                    backup_message = {'type': 'error', 'text': 'Name and backup selection are required'}
                else:
                    # Get the backup object
                    backup = BackupFile.objects.get(id=backup_id)
                    
                    # Create restore point
                    restore_point = RestorePoint(
                        name=name,
                        backup=backup,
                        note=note
                    )
                    restore_point.save()
                    backup_message = {'type': 'success', 'text': 'Restore point created successfully.'}
            except BackupFile.DoesNotExist:
                backup_message = {'type': 'error', 'text': 'Selected backup does not exist'}
            except Exception as e:
                backup_message = {'type': 'error', 'text': f'Error creating restore point: {str(e)}'}
        
        # Handle restore execution
        if request.method == 'POST' and 'execute_restore' in request.POST:
            restore_id = request.POST.get('restore_id')
            confirmation = request.POST.get('confirm_restore')
            
            if restore_id and confirmation == 'confirm':
                restore_point = RestorePoint.objects.get(id=restore_id)
                success, message = restore_backup(restore_point)
                
                if success:
                    restore_message = {'type': 'success', 'text': 'Restore completed successfully.'}
                else:
                    restore_message = {'type': 'error', 'text': f'Error during restore: {message}'}
        
        # Handle schedule creation/editing
        if request.method == 'POST' and 'save_schedule' in request.POST:
            schedule_id = request.POST.get('schedule_id')
            
            if schedule_id:
                # Editing existing schedule
                schedule = BackupSchedule.objects.get(id=schedule_id)
                schedule_form = BackupScheduleForm(request.POST, instance=schedule)
            else:
                # Creating new schedule
                schedule_form = BackupScheduleForm(request.POST)
                
            if schedule_form.is_valid():
                schedule_form.save()
                backup_message = {'type': 'success', 'text': 'Backup schedule saved successfully.'}
        else:
            schedule_form = BackupScheduleForm()
            
        # Get backup statistics
        try:
            from backup.models import BackupFile, RestorePoint, BackupSchedule
            from django.db.models import Sum
            
            # Count backups
            total_backups = BackupFile.objects.count()
            successful_backups = BackupFile.objects.filter(status='completed').count()
            
            # Calculate total size
            total_size = BackupFile.objects.filter(status='completed').aggregate(Sum('size'))['size__sum'] or 0
            
            # Get recent backups
            recent_backups = BackupFile.objects.all().order_by('-created_at')[:10]
            
            # Get all backups for the restore form
            backups = BackupFile.objects.filter(status='completed').order_by('-created_at')
            
            # Get restore points
            restore_points = RestorePoint.objects.all().order_by('-created_at')
            
            # Get backup schedules
            backup_schedules = BackupSchedule.objects.all().order_by('-created_at')
            
            backup_context = {
                'backup_message': backup_message,
                'recent_backups': recent_backups,
                'backups': backups,  # For the restore form dropdown
                'restore_points': restore_points,
                'backup_schedules': backup_schedules,
                'backup_stats': {
                    'total_backups': total_backups,
                    'successful_backups': successful_backups,
                    'total_size': total_size,
                    'total_size_mb': round(total_size / (1024 * 1024), 2) if total_size else 0,
                }
            }
        except (ImportError, ModuleNotFoundError):
            # Backup app not fully installed yet
            backup_context = {
                'backup_app_missing': True
            }
        
    except Exception as e:
        # If anything goes wrong, show error message
        backup_context = {
            'backup_app_missing': True,
            'backup_message': {'type': 'error', 'text': f'Error: {str(e)}'}
        }
    
    # Handle SEO functionality
    seo_context = {}
    try:
        from django.utils import timezone
        from seo.models import SeoMetadata, SeoScore, SeoIssue, Keyword, SitemapConfig
        from seo.forms import SitemapConfigForm
        from seo.utils import generate_sitemap, ping_search_engines
        
        # Handle sitemap configuration form submission
        if request.method == 'POST' and 'save_sitemap' in request.POST:
            # Get or create sitemap config
            config, created = SitemapConfig.objects.get_or_create(pk=1)
            
            # Update fields
            config.include_blog_posts = 'include_blog_posts' in request.POST
            config.include_pages = 'include_pages' in request.POST
            config.include_categories = 'include_categories' in request.POST
            config.auto_ping_search_engines = 'auto_ping_search_engines' in request.POST
            config.blog_update_frequency = request.POST.get('blog_update_frequency', 'weekly')
            config.pages_update_frequency = request.POST.get('pages_update_frequency', 'monthly')
            config.categories_update_frequency = request.POST.get('categories_update_frequency', 'monthly')
            config.save()
            
            # Generate sitemap if requested
            if 'generate' in request.POST:
                # Absolute URL to sitemap
                sitemap_url = request.build_absolute_uri('/sitemap.xml')
                
                # Generate sitemap
                sitemap_urls = generate_sitemap(config)
                
                # Update last generated time
                config.last_generated = timezone.now()
                config.save()
                
                # Ping search engines if enabled
                if config.auto_ping_search_engines:
                    ping_results = ping_search_engines(sitemap_url)
                    
                    # Add a message about ping results
                    ping_message = 'Search engines notified: '
                    for engine, result in ping_results.items():
                        ping_message += f'{engine} ("{result["message"]}"), '
                    
                    messages.info(request, ping_message[:-2])  # Remove last comma and space
                
                messages.success(request, f'Sitemap generated with {len(sitemap_urls)} URLs')
            else:
                messages.success(request, 'Sitemap configuration saved successfully.')
        
        # Get SEO stats
        avg_score = SeoScore.objects.all().values_list('overall_score', flat=True)
        if avg_score.exists():
            avg_score = round(sum(avg_score) / len(avg_score), 1)
        else:
            avg_score = 'N/A'
        
        # Get optimized pages count
        optimized_pages = SeoMetadata.objects.count()
        
        # Get critical issues count
        critical_issues = SeoIssue.objects.filter(severity__in=['critical', 'high'], resolved=False).count()
        
        # Combine stats
        seo_stats = {
            'avg_score': avg_score,
            'optimized_pages': optimized_pages,
            'critical_issues': critical_issues
        }
        
        # Get sitemap config
        sitemap_config, created = SitemapConfig.objects.get_or_create(pk=1)
        
        # Get top keywords
        top_keywords = Keyword.objects.filter(is_primary=True).order_by('-usage_count')[:10]
        
        # Sitemap URL
        sitemap_url = request.build_absolute_uri('/sitemap.xml')
        
        seo_context = {
            'seo_app_missing': False,
            'seo_stats': seo_stats,
            'sitemap_config': sitemap_config,
            'top_keywords': top_keywords,
            'sitemap_url': sitemap_url,
        }
    except (ImportError, ModuleNotFoundError):
        seo_context = {
            'seo_app_missing': True
        }
    
    context = {
        'active_tab': 'settings',
        **backup_context,
        **seo_context
    }
    
    return render(request, 'admin/admin_settings.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def admin_analytics(request):
    """Admin view for analytics dashboard"""
    # Get time range from query params or default to 30 days
    days = int(request.GET.get('days', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # Get basic stats
    total_views = PageView.objects.count()
    total_users = User.objects.count()
    total_comments = Comment.objects.count()
    
    # Get trending posts (most viewed in time period)
    post_view_counts = {}
    post_views = PageView.objects.filter(
        timestamp__range=(start_date, end_date),
        path__startswith='/blog/'
    )
    
    for view in post_views:
        post_slug = view.path.split('/')[-1]
        if post_slug in post_view_counts:
            post_view_counts[post_slug] += 1
        else:
            post_view_counts[post_slug] = 1
    
    trending_posts = []
    for slug, count in sorted(post_view_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        try:
            post = BlogPost.objects.get(slug=slug)
            trending_posts.append({
                'title': post.title,
                'views': count,
                'url': f'/blog/{post.slug}/'
            })
        except BlogPost.DoesNotExist:
            continue
    
    context = {
        'active_tab': 'analytics',
        'title': 'Analytics Dashboard',
        'total_views': total_views,
        'total_users': total_users,
        'total_comments': total_comments,
        'trending_posts': trending_posts,
        'days': days
    }
    
    return render(request, 'admin/admin_analytics.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def get_analytics_data(request):
    """API endpoint for fetching analytics data"""
    # ... (rest of the code remains the same)
    days = int(request.GET.get('days', 30))
    end_date = timezone.now()
    start_date = end_date - timedelta(days=days)
    
    # 1. Post views over time
    post_views_data = PageView.objects.filter(
        timestamp__range=(start_date, end_date),
        path__startswith='/blog/'
    ).values('timestamp__date').annotate(
        count=Count('id')
    ).order_by('timestamp__date')
    
    post_views = [{
        'date': entry['timestamp__date'].strftime('%Y-%m-%d'),
        'count': entry['count']
    } for entry in post_views_data]
    
    # 2. User registration trends
    user_reg_data = User.objects.filter(
        date_joined__range=(start_date, end_date)
    ).values('date_joined__date').annotate(
        count=Count('id')
    ).order_by('date_joined__date')
    
    user_registrations = [{
        'date': entry['date_joined__date'].strftime('%Y-%m-%d'),
        'count': entry['count']
    } for entry in user_reg_data]
    
    # 3. Comment activity metrics
    comment_data = Comment.objects.filter(
        created_at__range=(start_date, end_date)
    ).values('created_at__date').annotate(
        count=Count('id')
    ).order_by('created_at__date')
    
    comment_activity = [{
        'date': entry['created_at__date'].strftime('%Y-%m-%d'),
        'count': entry['count']
    } for entry in comment_data]
    
    # 4. Category popularity statistics
    category_data = BlogPost.objects.filter(
        created_at__range=(start_date, end_date)
    ).values('category__name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    category_stats = [{
        'name': entry['category__name'] if entry['category__name'] else 'Uncategorized',
        'count': entry['count']
    } for entry in category_data]
    
    # 5. Real-time visitor data (last 24 hours by hour)
    last_day = timezone.now() - timedelta(days=1)
    hourly_views = PageView.objects.filter(
        timestamp__gte=last_day
    ).extra({
        'hour': "STRFTIME('%H', timestamp)"
    }).values('hour').annotate(
        count=Count('id')
    ).order_by('hour')
    
    hourly_visitors = [{
        'hour': entry['hour'],
        'count': entry['count']
    } for entry in hourly_views]
    
    # 6. Traffic sources (referer domains)
    # This would require storing referrer information in PageView model
    # For demonstration, we'll use placeholder data
    traffic_sources = [
        {'source': 'Direct', 'count': 45},
        {'source': 'Google', 'count': 32},
        {'source': 'Social Media', 'count': 18},
        {'source': 'Other', 'count': 5}
    ]
    
    # 7. Browser/device statistics
    # This would require storing user agent information in PageView model
    # For demonstration, we'll use placeholder data
    device_stats = [
        {'device': 'Desktop', 'count': 65},
        {'device': 'Mobile', 'count': 30},
        {'device': 'Tablet', 'count': 5}
    ]
    
    data = {
        'success': True,
        'post_views': post_views,
        'user_registrations': user_registrations,
        'comment_activity': comment_activity,
        'category_stats': category_stats,
        'hourly_visitors': hourly_visitors,
        'traffic_sources': traffic_sources,
        'device_stats': device_stats
    }

    return JsonResponse(data)

# Notifications system removed as requested
