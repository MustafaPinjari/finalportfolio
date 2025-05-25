import re
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from .models import SeoScore, SeoIssue

def analyze_content(content, target_keywords=None):
    """
    Analyze content for SEO issues including keyword density and readability
    
    Returns a dict with analysis results
    """
    results = {
        'word_count': 0,
        'keyword_density': {},
        'readability_score': 0,
        'has_headings': False,
        'heading_structure': [],
        'issues': [],
    }
    
    if not content:
        results['issues'].append({
            'type': 'content',
            'severity': 'high',
            'message': 'No content to analyze'
        })
        return results
    
    # Count words
    words = re.findall(r'\w+', content.lower())
    results['word_count'] = len(words)
    
    if results['word_count'] < 300:
        results['issues'].append({
            'type': 'content',
            'severity': 'medium',
            'message': f'Content is too short ({results["word_count"]} words, aim for 300+)'
        })
    
    # Check keyword density if target keywords provided
    if target_keywords:
        for keyword in target_keywords:
            # Count occurrences of each keyword
            keyword_lower = keyword.lower()
            count = content.lower().count(keyword_lower)
            density = (count / results['word_count']) * 100 if results['word_count'] > 0 else 0
            results['keyword_density'][keyword] = density
            
            # Check if keyword density is appropriate
            if density > 5:
                results['issues'].append({
                    'type': 'keyword',
                    'severity': 'medium',
                    'message': f'Keyword "{keyword}" density is too high ({density:.1f}%)'
                })
            elif density == 0:
                results['issues'].append({
                    'type': 'keyword',
                    'severity': 'medium',
                    'message': f'Keyword "{keyword}" not found in content'
                })
    
    # Check for headings using basic regex
    heading_matches = re.findall(r'<h([1-6])[^>]*>(.+?)</h\1>', content, re.IGNORECASE)
    results['has_headings'] = len(heading_matches) > 0
    
    if not results['has_headings']:
        results['issues'].append({
            'type': 'content',
            'severity': 'medium',
            'message': 'No headings found in content'
        })
    else:
        # Extract heading structure
        for level, text in heading_matches:
            results['heading_structure'].append({
                'level': int(level),
                'text': text.strip()
            })
        
        # Check if H1 is present
        has_h1 = any(h['level'] == 1 for h in results['heading_structure'])
        if not has_h1:
            results['issues'].append({
                'type': 'content',
                'severity': 'medium',
                'message': 'No H1 heading found'
            })
    
    # Calculate very basic readability score (0-100)
    # This is a simplistic implementation - in production, you might want to use a more sophisticated algorithm
    avg_sentence_length = calculate_avg_sentence_length(content)
    avg_word_length = sum(len(word) for word in words) / len(words) if words else 0
    
    # Lower sentence and word length = better readability (simplistic approach)
    sentence_score = max(0, 100 - (avg_sentence_length - 15) * 5) if avg_sentence_length > 15 else 100
    word_score = max(0, 100 - (avg_word_length - 5) * 10) if avg_word_length > 5 else 100
    
    results['readability_score'] = int((sentence_score + word_score) / 2)
    
    if results['readability_score'] < 60:
        results['issues'].append({
            'type': 'content',
            'severity': 'medium',
            'message': 'Content may be difficult to read. Consider shorter sentences and simpler words.'
        })
    
    return results

def calculate_avg_sentence_length(text):
    """
    Calculate average sentence length from text
    """
    # Simple sentence splitting - this is basic and would need improvement for production use
    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]
    
    if not sentences:
        return 0
    
    words_per_sentence = [len(re.findall(r'\w+', s)) for s in sentences]
    return sum(words_per_sentence) / len(sentences) if sentences else 0

def analyze_meta_tags(metadata):
    """
    Analyze SEO metadata for issues
    
    Returns a dict with analysis results
    """
    results = {
        'issues': [],
    }
    
    # Check meta title
    if not metadata.meta_title:
        results['issues'].append({
            'type': 'meta',
            'severity': 'high',
            'message': 'Meta title is missing'
        })
    elif len(metadata.meta_title) < 30:
        results['issues'].append({
            'type': 'meta',
            'severity': 'medium',
            'message': f'Meta title is too short ({len(metadata.meta_title)} chars, aim for 50-60)'
        })
    elif len(metadata.meta_title) > 70:
        results['issues'].append({
            'type': 'meta',
            'severity': 'medium',
            'message': f'Meta title is too long ({len(metadata.meta_title)} chars, aim for 50-60)'
        })
    
    # Check meta description
    if not metadata.meta_description:
        results['issues'].append({
            'type': 'meta',
            'severity': 'medium',
            'message': 'Meta description is missing'
        })
    elif len(metadata.meta_description) < 80:
        results['issues'].append({
            'type': 'meta',
            'severity': 'low',
            'message': f'Meta description is too short ({len(metadata.meta_description)} chars, aim for 120-160)'
        })
    elif len(metadata.meta_description) > 160:
        results['issues'].append({
            'type': 'meta',
            'severity': 'low',
            'message': f'Meta description is too long ({len(metadata.meta_description)} chars, aim for 120-160)'
        })
    
    # Check meta keywords
    if not metadata.meta_keywords:
        results['issues'].append({
            'type': 'meta',
            'severity': 'low',
            'message': 'Meta keywords are missing'
        })
    
    # Check for noindex/nofollow
    if metadata.no_index:
        results['issues'].append({
            'type': 'meta',
            'severity': 'info',
            'message': 'Page is set to noindex (will not appear in search results)'
        })
    
    if metadata.no_follow:
        results['issues'].append({
            'type': 'meta',
            'severity': 'info',
            'message': 'Page is set to nofollow (search engines will not follow links)'
        })
    
    # Check social media tags
    if not metadata.og_title and not metadata.og_description:
        results['issues'].append({
            'type': 'meta',
            'severity': 'low',
            'message': 'Open Graph tags are missing (affects social media sharing)'
        })
    
    if not metadata.twitter_title and not metadata.twitter_description:
        results['issues'].append({
            'type': 'meta',
            'severity': 'low',
            'message': 'Twitter Card tags are missing (affects Twitter sharing)'
        })
    
    return results

def check_technical_seo(url):
    """
    Check technical SEO aspects of a URL
    
    Returns a dict with analysis results
    """
    results = {
        'issues': [],
        'load_time': None,
        'status_code': None,
    }
    
    try:
        # Make a request to the URL
        response = requests.get(url, timeout=10)
        results['status_code'] = response.status_code
        
        if response.status_code != 200:
            results['issues'].append({
                'type': 'technical',
                'severity': 'critical',
                'message': f'Page returns HTTP status {response.status_code}'
            })
            return results
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Check canonical URL
        canonical = soup.find('link', rel='canonical')
        if not canonical:
            results['issues'].append({
                'type': 'technical',
                'severity': 'medium',
                'message': 'No canonical URL specified'
            })
        elif canonical.get('href') != url:
            results['issues'].append({
                'type': 'technical',
                'severity': 'info',
                'message': f'Canonical URL points to a different URL: {canonical.get("href")}'
            })
        
        # Check for mobile friendliness (basic viewport check)
        viewport = soup.find('meta', attrs={'name': 'viewport'})
        if not viewport:
            results['issues'].append({
                'type': 'technical',
                'severity': 'medium',
                'message': 'No viewport meta tag found (affects mobile usability)'
            })
        
        # Check for broken links (limited to a few to avoid excessive requests)
        links = soup.find_all('a', href=True)[:10]  # Limit to first 10 links
        for link in links:
            href = link.get('href')
            if href.startswith('http'):
                try:
                    head_response = requests.head(href, timeout=5)
                    if head_response.status_code >= 400:
                        results['issues'].append({
                            'type': 'technical',
                            'severity': 'medium',
                            'message': f'Broken link found: {href} (status {head_response.status_code})'
                        })
                except requests.RequestException:
                    results['issues'].append({
                        'type': 'technical',
                        'severity': 'medium',
                        'message': f'Could not access link: {href}'
                    })
    
    except requests.RequestException as e:
        results['issues'].append({
            'type': 'technical',
            'severity': 'critical',
            'message': f'Error accessing URL: {str(e)}'
        })
    
    return results

def run_seo_analysis(metadata, content, url):
    """
    Run a comprehensive SEO analysis and store results
    
    Returns a dict with all analysis results and the created/updated score object
    """
    # Get primary keywords
    primary_keywords = list(metadata.keywords.filter(is_primary=True).values_list('keyword', flat=True))
    
    # Run all analyses
    content_analysis = analyze_content(content, primary_keywords)
    meta_analysis = analyze_meta_tags(metadata)
    technical_analysis = check_technical_seo(url)
    
    # Collect all issues
    all_issues = (
        content_analysis['issues'] + 
        meta_analysis['issues'] + 
        technical_analysis['issues']
    )
    
    # Calculate scores
    content_score = 100 - (len(content_analysis['issues']) * 10)
    meta_score = 100 - (len(meta_analysis['issues']) * 15)
    technical_score = 100 - (len(technical_analysis['issues']) * 20)
    
    # Ensure scores are within 0-100 range
    content_score = max(0, min(100, content_score))
    meta_score = max(0, min(100, meta_score))
    technical_score = max(0, min(100, technical_score))
    
    # Calculate overall score (weighted average)
    overall_score = (
        (content_score * 0.4) + 
        (meta_score * 0.3) + 
        (technical_score * 0.3)
    )
    overall_score = int(overall_score)
    
    # Create or update the score object
    score, created = SeoScore.objects.update_or_create(
        metadata=metadata,
        defaults={
            'overall_score': overall_score,
            'content_score': content_score,
            'technical_score': technical_score,
            'analyzed_at': timezone.now()
        }
    )
    
    # Clear existing issues and create new ones
    score.issues.all().delete()
    
    for issue in all_issues:
        SeoIssue.objects.create(
            score=score,
            issue_type=issue['type'],
            severity=issue['severity'],
            message=issue['message']
        )
    
    # Update keyword usage count
    if primary_keywords and content:
        for keyword in metadata.keywords.all():
            keyword_lower = keyword.keyword.lower()
            keyword.usage_count = content.lower().count(keyword_lower)
            keyword.save()
    
    return {
        'score': score,
        'content_analysis': content_analysis,
        'meta_analysis': meta_analysis,
        'technical_analysis': technical_analysis,
        'issues_count': len(all_issues)
    }

def generate_sitemap(config=None):
    """
    Generate sitemap data based on configuration
    
    Returns a list of dict objects with loc, lastmod, changefreq, priority
    """
    sitemap_data = []
    
    # If no config is provided, include all by default
    include_blog_posts = True
    include_pages = True
    include_categories = True
    blog_freq = 'weekly'
    pages_freq = 'monthly'
    categories_freq = 'monthly'
    
    if config:
        include_blog_posts = config.include_blog_posts
        include_pages = config.include_pages
        include_categories = config.include_categories
        blog_freq = config.blog_update_frequency
        pages_freq = config.pages_update_frequency
        categories_freq = config.categories_update_frequency
    
    # Start with homepage
    site_url = 'http://example.com'  # Replace with actual site URL from settings
    if hasattr(settings, 'SITE_URL'):
        site_url = settings.SITE_URL
    
    sitemap_data.append({
        'loc': site_url,
        'lastmod': timezone.now().strftime('%Y-%m-%d'),
        'changefreq': 'daily',
        'priority': 1.0
    })
    
    # Add blog posts
    if include_blog_posts:
        try:
            # Try to import the BlogPost model
            from blog.models import BlogPost
            
            # Get all blog posts - since there's no 'published' field
            # we'll include all posts
            for post in BlogPost.objects.all().order_by('-created_at'):
                sitemap_data.append({
                    'loc': urljoin(site_url, f'/blog/{post.slug}/'),
                    'lastmod': post.updated_at.strftime('%Y-%m-%d') if post.updated_at else post.created_at.strftime('%Y-%m-%d'),
                    'changefreq': blog_freq,
                    'priority': 0.8
                })
        except (ImportError, ModuleNotFoundError):
            # Blog app or model doesn't exist, skip
            pass
    
    # Add categories
    if include_categories:
        try:
            # Try to import the Category model
            from blog.models import Category
            
            for category in Category.objects.all():
                sitemap_data.append({
                    'loc': urljoin(site_url, f'/blog/category/{category.slug}/'),
                    'lastmod': timezone.now().strftime('%Y-%m-%d'),
                    'changefreq': categories_freq,
                    'priority': 0.7
                })
        except (ImportError, ModuleNotFoundError):
            # Category model doesn't exist, skip
            pass
    
    # Add pages (if you have a Page model)
    if include_pages:
        # Since we don't know if there's a Page model, try to get pages from the database
        try:
            # Look for a model called Page in any installed app
            page_models = []
            for ct in ContentType.objects.all():
                if ct.model == 'page':
                    page_models.append(ct.model_class())
            
            for Page in page_models:
                for page in Page.objects.all():
                    sitemap_data.append({
                        'loc': urljoin(site_url, f'/{page.slug}/'),
                        'lastmod': page.updated_at.strftime('%Y-%m-%d') if hasattr(page, 'updated_at') else timezone.now().strftime('%Y-%m-%d'),
                        'changefreq': pages_freq,
                        'priority': 0.6
                    })
        except Exception:
            # No Page model or error, skip
            pass
    
    # Update config's last_generated timestamp if provided
    if config:
        config.last_generated = timezone.now()
        config.save()
    
    return sitemap_data

def ping_search_engines(sitemap_url):
    """
    Ping search engines to notify them of an updated sitemap
    
    Returns a dict with status of each ping
    """
    engines = {
        'Google': f'https://www.google.com/ping?sitemap={sitemap_url}',
        'Bing': f'https://www.bing.com/ping?sitemap={sitemap_url}'
    }
    
    results = {}
    
    for engine, ping_url in engines.items():
        try:
            response = requests.get(ping_url, timeout=10)
            if response.status_code == 200:
                results[engine] = {
                    'success': True,
                    'message': 'Successfully pinged'
                }
            else:
                results[engine] = {
                    'success': False,
                    'message': f'Failed with status code {response.status_code}'
                }
        except requests.RequestException as e:
            results[engine] = {
                'success': False,
                'message': f'Error: {str(e)}'
            }
    
    return results
