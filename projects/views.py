from django.shortcuts import render, get_object_or_404
from blog.models import Project, Category

def projects(request):
    """
    View for displaying all projects
    """
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
    
    return render(request, 'projects/projects.html', context)

def project_detail(request, slug):
    """
    View for displaying a single project's details
    """
    # Get the requested project
    project = get_object_or_404(Project, slug=slug)
    
    # Get related projects (same category, excluding current project)
    related_projects = []
    if project.category:
        related_projects = Project.objects.filter(category=project.category).exclude(id=project.id)[:3]
    
    context = {
        'project': project,
        'related_projects': related_projects
    }
    
    return render(request, 'projects/project_detail.html', context)
