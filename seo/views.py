from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.urls import reverse
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.views.decorators.http import require_GET
from django.template.loader import render_to_string
from django.conf import settings
import re

from .models import SeoMetadata, SeoScore, SeoIssue, Keyword, SitemapConfig
from .forms import SeoMetadataForm, KeywordFormSet, SitemapConfigForm
from .utils import run_seo_analysis, generate_sitemap, ping_search_engines

# Decorator for checking admin or staff status
def is_admin_or_staff(user):
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@login_required
@user_passes_test(is_admin_or_staff)
def admin_seo_dashboard(request):
    """SEO Dashboard view"""
    # Get latest SEO scores
    recent_scores = SeoScore.objects.all().order_by('-analyzed_at')[:10]
    
    # Get critical and high severity issues
    critical_issues = SeoIssue.objects.filter(severity__in=['critical', 'high'], resolved=False)
    
    # Get sitemap config
    sitemap_config, created = SitemapConfig.objects.get_or_create(pk=1)
    
    context = {
        'active_tab': 'seo',  # For highlighting the SEO tab in the admin sidebar
        'recent_scores': recent_scores,
        'critical_issues': critical_issues,
        'sitemap_config': sitemap_config,
    }
    
    return render(request, 'admin/admin_seo_dashboard.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def edit_seo_metadata(request, content_type_id, object_id):
    """Edit SEO metadata for any content type"""
    content_type = get_object_or_404(ContentType, id=content_type_id)
    content_object = get_object_or_404(content_type.model_class(), id=object_id)
    
    # Get or create SEO metadata
    metadata, created = SeoMetadata.objects.get_or_create(
        content_type=content_type,
        object_id=object_id
    )
    
    # Initialize keyword formset
    KeywordFormSet.extra = 3
    keyword_formset = KeywordFormSet(
        request.POST or None,
        queryset=metadata.keywords.all(),
        prefix='keywords'
    )
    
    if request.method == 'POST':
        form = SeoMetadataForm(request.POST, request.FILES, instance=metadata)
        
        if form.is_valid() and keyword_formset.is_valid():
            metadata = form.save()
            
            # Save keywords
            keywords = keyword_formset.save(commit=False)
            for keyword in keywords:
                keyword.metadata = metadata
                keyword.save()
            
            # Handle deleted keywords
            for obj in keyword_formset.deleted_objects:
                obj.delete()
                
            # Run SEO analysis if requested
            if 'analyze' in request.POST:
                # Get content and URL
                if hasattr(content_object, 'get_absolute_url'):
                    url = request.build_absolute_uri(content_object.get_absolute_url())
                else:
                    url = request.build_absolute_uri('/')
                
                # Get content
                if hasattr(content_object, 'content'):
                    content = content_object.content
                elif hasattr(content_object, 'body'):
                    content = content_object.body
                else:
                    content = ''
                
                # Run analysis
                analysis_result = run_seo_analysis(metadata, content, url)
                
                # Add message
                score = analysis_result['score']
                messages.success(
                    request, 
                    f'SEO analysis complete. Overall score: {score.overall_score}/100'
                )
            
            # Add success message
            messages.success(request, f'SEO metadata for {content_object} updated successfully')
            
            # Redirect to the appropriate page
            return redirect('seo:edit_metadata', content_type_id=content_type_id, object_id=object_id)
    else:
        form = SeoMetadataForm(instance=metadata)
    
    # Get SEO score if available
    try:
        seo_score = metadata.score
        has_score = True
    except SeoScore.DoesNotExist:
        seo_score = None
        has_score = False
    
    # Get issues if available
    if has_score:
        issues = seo_score.issues.all().order_by('-severity', 'issue_type')
    else:
        issues = []
    
    context = {
        'active_tab': 'seo',
        'form': form,
        'keyword_formset': keyword_formset,
        'metadata': metadata,
        'content_object': content_object,
        'content_type': content_type,
        'seo_score': seo_score,
        'has_score': has_score,
        'issues': issues,
    }
    
    return render(request, 'admin/admin_seo_editor.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def run_analysis(request, metadata_id):
    """Run SEO analysis on a page"""
    metadata = get_object_or_404(SeoMetadata, id=metadata_id)
    content_object = metadata.content_object
    
    if request.method == 'POST':
        # Get content and URL
        if hasattr(content_object, 'get_absolute_url'):
            url = request.build_absolute_uri(content_object.get_absolute_url())
        else:
            url = request.build_absolute_uri('/')
        
        # Get content
        if hasattr(content_object, 'content'):
            content = content_object.content
        elif hasattr(content_object, 'body'):
            content = content_object.body
        else:
            content = ''
        
        # Run analysis
        analysis_result = run_seo_analysis(metadata, content, url)
        
        # Redirect back to metadata editor
        content_type_id = ContentType.objects.get_for_model(content_object).id
        object_id = content_object.id
        
        messages.success(
            request, 
            f'SEO analysis complete. Overall score: {analysis_result["score"].overall_score}/100'
        )
        
        return redirect('seo:edit_metadata', content_type_id=content_type_id, object_id=object_id)
    
    # If not a POST request, redirect to the dashboard
    return redirect('seo:dashboard')

@login_required
@user_passes_test(is_admin_or_staff)
def resolve_issue(request, issue_id):
    """Mark an SEO issue as resolved"""
    issue = get_object_or_404(SeoIssue, id=issue_id)
    
    if request.method == 'POST':
        issue.resolved = not issue.resolved  # Toggle resolved status
        issue.save()
        
        # Return JSON response for AJAX calls
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'resolved': issue.resolved,
                'issue_id': issue.id
            })
    
    # Get metadata info for redirect
    metadata = issue.score.metadata
    content_type_id = metadata.content_type_id
    object_id = metadata.object_id
    
    return redirect('seo:edit_metadata', content_type_id=content_type_id, object_id=object_id)

@login_required
@user_passes_test(is_admin_or_staff)
def manage_sitemap(request):
    """Manage sitemap configuration"""
    # Get or create sitemap config
    config, created = SitemapConfig.objects.get_or_create(pk=1)
    
    if request.method == 'POST':
        form = SitemapConfigForm(request.POST, instance=config)
        
        if form.is_valid():
            form.save()
            
            # Generate sitemap if requested
            if 'generate' in request.POST:
                sitemap_url = request.build_absolute_uri(reverse('seo:sitemap_xml'))
                
                # Ping search engines if enabled
                if config.auto_ping_search_engines:
                    ping_results = ping_search_engines(sitemap_url)
                    
                    # Create message about ping results
                    ping_message = 'Search engines notified: '
                    for engine, result in ping_results.items():
                        ping_message += f'{engine} ("{result["message"]}"), '
                    
                    messages.info(request, ping_message[:-2])  # Remove last comma and space
                
                messages.success(request, 'Sitemap configuration saved and sitemap generated successfully.')
            else:
                messages.success(request, 'Sitemap configuration saved successfully.')
            
            return redirect('seo:manage_sitemap')
    else:
        form = SitemapConfigForm(instance=config)
    
    # Generate preview of sitemap
    sitemap_preview = generate_sitemap(config)
    
    context = {
        'active_tab': 'seo',
        'form': form,
        'config': config,
        'sitemap_preview': sitemap_preview[:10],  # Limit to first 10 entries
        'sitemap_count': len(sitemap_preview),
        'sitemap_url': request.build_absolute_uri(reverse('seo:sitemap_xml')),
    }
    
    return render(request, 'admin/admin_sitemap_config.html', context)

@require_GET
def sitemap_xml(request):
    """Generate and serve sitemap XML"""
    # Get sitemap config
    try:
        config = SitemapConfig.objects.get(pk=1)
    except SitemapConfig.DoesNotExist:
        config = None
    
    # Generate sitemap data
    urls = generate_sitemap(config)
    
    # Render sitemap XML
    xml_content = render_to_string('seo/sitemap.xml', {'urls': urls})
    
    return HttpResponse(xml_content, content_type='application/xml')

@login_required
@user_passes_test(is_admin_or_staff)
def keyword_analysis(request):
    """Keyword analysis dashboard"""
    # Get all keywords grouped by content type
    keywords = Keyword.objects.filter(is_primary=True).order_by('-usage_count')
    
    context = {
        'active_tab': 'seo',
        'keywords': keywords,
    }
    
    return render(request, 'admin/admin_keyword_analysis.html', context)

@login_required
@user_passes_test(is_admin_or_staff)
def real_time_seo_check(request):
    """Real-time SEO check via AJAX"""
    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        title = request.POST.get('title', '')
        description = request.POST.get('description', '')
        keywords = request.POST.get('keywords', '')
        content = request.POST.get('content', '')
        
        # Basic checks
        issues = []
        score = 100
        
        # Title checks
        if not title:
            issues.append({
                'type': 'meta',
                'severity': 'high',
                'message': 'Meta title is missing'
            })
            score -= 20
        elif len(title) < 30:
            issues.append({
                'type': 'meta',
                'severity': 'medium',
                'message': f'Meta title is too short ({len(title)} chars, aim for 50-60)'
            })
            score -= 10
        elif len(title) > 70:
            issues.append({
                'type': 'meta',
                'severity': 'medium',
                'message': f'Meta title is too long ({len(title)} chars, aim for 50-60)'
            })
            score -= 10
        
        # Description checks
        if not description:
            issues.append({
                'type': 'meta',
                'severity': 'medium',
                'message': 'Meta description is missing'
            })
            score -= 15
        elif len(description) < 80:
            issues.append({
                'type': 'meta',
                'severity': 'low',
                'message': f'Meta description is too short ({len(description)} chars, aim for 120-160)'
            })
            score -= 5
        elif len(description) > 160:
            issues.append({
                'type': 'meta',
                'severity': 'low',
                'message': f'Meta description is too long ({len(description)} chars, aim for 120-160)'
            })
            score -= 5
        
        # Keywords check
        if not keywords:
            issues.append({
                'type': 'keyword',
                'severity': 'low',
                'message': 'No keywords specified'
            })
            score -= 5
        
        # Content checks
        if content:
            word_count = len(re.findall(r'\w+', content))
            if word_count < 300:
                issues.append({
                    'type': 'content',
                    'severity': 'medium',
                    'message': f'Content is too short ({word_count} words, aim for 300+)'
                })
                score -= 10
        
        # Ensure score is between 0-100
        score = max(0, min(100, score))
        
        # Determine color based on score
        if score >= 80:
            color = 'success'
        elif score >= 50:
            color = 'warning'
        else:
            color = 'danger'
        
        return JsonResponse({
            'score': score,
            'color': color,
            'issues': issues
        })
    
    # Return error for non-AJAX or non-POST requests
    return JsonResponse({'error': 'Invalid request'}, status=400)
