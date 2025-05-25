from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from blog.models import Project, Category, ProjectScreenshot
from django.http import JsonResponse
import os
from django.conf import settings
import uuid

@login_required
def admin_projects(request):
    """
    Admin dashboard for project management
    """
    # Ensure user is staff
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
        
    # Get all projects
    projects = Project.objects.all().order_by('-created_at')
    
    # Get categories for filtering
    categories = Category.objects.all()
    
    # Handle category filtering if present in request
    category_slug = request.GET.get('category')
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        projects = projects.filter(category=category)
    
    context = {
        'active_tab': 'projects',
        'projects': projects,
        'categories': categories,
        'selected_category': category_slug
    }
    
    return render(request, 'admin/admin_projects.html', context)

@login_required
def admin_project_form(request, project_id=None):
    """
    Form for adding or editing a project
    """
    # Ensure user is staff
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    # Get project if editing, otherwise None for a new project
    project = None
    if project_id:
        project = get_object_or_404(Project, id=project_id)
    
    # Get all categories
    categories = Category.objects.all()
    
    # Handle form submission
    if request.method == 'POST':
        # Get form data
        title = request.POST.get('title')
        description = request.POST.get('description')
        content = request.POST.get('content')
        features = request.POST.get('features')
        technologies = request.POST.get('technologies')
        github_link = request.POST.get('github_link')
        live_link = request.POST.get('live_link')
        category_id = request.POST.get('category')
        featured = request.POST.get('featured') == 'on'
        
        # Create or update project
        if project:
            # Update existing project
            project.title = title
            project.description = description
            project.content = content
            project.features = features
            project.technologies = technologies
            project.github_link = github_link
            project.live_link = live_link
            project.featured = featured
            
            if category_id:
                project.category = get_object_or_404(Category, id=category_id)
            
            # Handle image upload if provided
            if request.FILES.get('image'):
                # Delete old image if it exists
                if project.image:
                    try:
                        if os.path.isfile(os.path.join(settings.MEDIA_ROOT, project.image.path)):
                            os.remove(os.path.join(settings.MEDIA_ROOT, project.image.path))
                    except (FileNotFoundError, ValueError):
                        pass
                project.image = request.FILES.get('image')
            
            project.save()
            messages.success(request, 'Project updated successfully!')
        else:
            # Create new project
            if not request.FILES.get('image'):
                messages.error(request, 'Image is required for a new project.')
                return redirect('projects:admin_project_add')
                
            new_project = Project(
                title=title,
                description=description,
                content=content,
                features=features,
                technologies=technologies,
                github_link=github_link,
                live_link=live_link,
                featured=featured,
                image=request.FILES.get('image')
            )
            
            if category_id:
                new_project.category = get_object_or_404(Category, id=category_id)
                
            new_project.save()
            messages.success(request, 'Project created successfully!')
        
        return redirect('projects:admin_projects')
    
    context = {
        'active_tab': 'projects',
        'project': project,
        'categories': categories,
        'is_edit': project is not None
    }
    
    return render(request, 'admin/admin_project_form.html', context)

@login_required
def delete_project(request, project_id):
    """
    Delete a project
    """
    # Ensure user is staff
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Permission denied'}, status=403)
    
    if request.method == 'POST':
        project = get_object_or_404(Project, id=project_id)
        
        # Delete image file if it exists
        if project.image:
            try:
                if os.path.isfile(os.path.join(settings.MEDIA_ROOT, project.image.path)):
                    os.remove(os.path.join(settings.MEDIA_ROOT, project.image.path))
            except (FileNotFoundError, ValueError):
                pass
        
        # Delete the project
        project.delete()
        
        return JsonResponse({'success': True, 'message': 'Project deleted successfully'})
    
    return JsonResponse({'success': False, 'message': 'Invalid request method'}, status=400)

@login_required
def admin_project_screenshots(request, project_id):
    """
    Manage project screenshots
    """
    # Ensure user is staff
    if not request.user.is_staff:
        messages.error(request, "You don't have permission to access this page.")
        return redirect('home')
    
    # Get project
    project = get_object_or_404(Project, id=project_id)
    screenshots = project.screenshots.all().order_by('order')
    
    # Handle screenshot creation
    if request.method == 'POST':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        size = request.POST.get('size', 'medium')
        order = request.POST.get('order', 0)
        image = request.FILES.get('image')
        
        if not image:
            messages.error(request, 'Image is required for a new screenshot.')
            return redirect('projects:admin_project_screenshots', project_id=project_id)
        
        # Create new screenshot
        screenshot = ProjectScreenshot(
            project=project,
            image=image,
            title=title,
            description=description,
            size=size,
            order=order
        )
        screenshot.save()
        messages.success(request, 'Screenshot added successfully!')
        return redirect('projects:admin_project_screenshots', project_id=project_id)
    
    # Screenshot deletion
    if request.method == 'DELETE' or (request.method == 'POST' and request.POST.get('_method') == 'DELETE'):
        screenshot_id = request.POST.get('screenshot_id') if request.method == 'POST' else request.GET.get('screenshot_id')
        if screenshot_id:
            screenshot = get_object_or_404(ProjectScreenshot, id=screenshot_id, project=project)
            
            # Delete image file if it exists
            if screenshot.image:
                try:
                    if os.path.isfile(os.path.join(settings.MEDIA_ROOT, screenshot.image.path)):
                        os.remove(os.path.join(settings.MEDIA_ROOT, screenshot.image.path))
                except (FileNotFoundError, ValueError):
                    pass
            
            # Delete the screenshot
            screenshot.delete()
            
            if request.method == 'DELETE':
                return JsonResponse({'success': True, 'message': 'Screenshot deleted successfully'})
            else:
                messages.success(request, 'Screenshot deleted successfully!')
                return redirect('projects:admin_project_screenshots', project_id=project_id)
    
    context = {
        'active_tab': 'projects',
        'project': project,
        'screenshots': screenshots,
        'size_choices': ProjectScreenshot._meta.get_field('size').choices
    }
    
    return render(request, 'admin/admin_project_screenshots.html', context)
