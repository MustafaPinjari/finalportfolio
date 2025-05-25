from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

class SeoMetadata(models.Model):
    """
    SEO metadata that can be associated with any content type
    """
    # Content type relations for generic relationship
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Basic SEO metadata
    meta_title = models.CharField(max_length=70, blank=True, null=True, 
                                help_text="Title for search engines (50-60 characters ideal)")
    meta_description = models.TextField(max_length=160, blank=True, null=True,
                                      help_text="Description for search engines (120-160 characters ideal)")
    meta_keywords = models.CharField(max_length=255, blank=True, null=True,
                                   help_text="Comma-separated keywords")
    
    # Open Graph metadata
    og_title = models.CharField(max_length=70, blank=True, null=True,
                              help_text="Title for social sharing")
    og_description = models.TextField(max_length=200, blank=True, null=True,
                                    help_text="Description for social sharing")
    og_image = models.ImageField(upload_to='seo/og_images/', blank=True, null=True,
                               help_text="Image for social sharing (1200x630 recommended)")
    
    # Twitter Card metadata
    twitter_title = models.CharField(max_length=70, blank=True, null=True)
    twitter_description = models.TextField(max_length=200, blank=True, null=True)
    twitter_image = models.ImageField(upload_to='seo/twitter_images/', blank=True, null=True,
                                    help_text="Image for Twitter cards (1200x600 recommended)")
    
    # Additional SEO fields
    canonical_url = models.URLField(blank=True, null=True,
                                  help_text="Canonical URL if different from the current URL")
    no_index = models.BooleanField(default=False, 
                                 help_text="Prevent search engines from indexing this page")
    no_follow = models.BooleanField(default=False,
                                  help_text="Prevent search engines from following links on this page")
    
    # Schema.org structured data (JSON-LD)
    structured_data = models.JSONField(blank=True, null=True, 
                                     help_text="JSON-LD structured data for rich results")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "SEO Metadata"
        verbose_name_plural = "SEO Metadata"
        unique_together = ('content_type', 'object_id')
    
    def __str__(self):
        return f"SEO for {self.content_object}"

class Keyword(models.Model):
    """
    Keywords associated with a specific metadata record
    """
    metadata = models.ForeignKey(SeoMetadata, on_delete=models.CASCADE, related_name='keywords')
    keyword = models.CharField(max_length=100)
    is_primary = models.BooleanField(default=False, 
                                   help_text="Primary/focus keyword for this content")
    usage_count = models.PositiveIntegerField(default=0, 
                                            help_text="How many times this keyword appears in content")
    
    class Meta:
        verbose_name = "Keyword"
        verbose_name_plural = "Keywords"
    
    def __str__(self):
        return self.keyword

class SeoScore(models.Model):
    """
    SEO score and analysis results for a metadata record
    """
    metadata = models.OneToOneField(SeoMetadata, on_delete=models.CASCADE, related_name='score')
    overall_score = models.PositiveIntegerField(default=0, help_text="Overall SEO score (0-100)")
    content_score = models.PositiveIntegerField(default=0, help_text="Content quality score (0-100)")
    technical_score = models.PositiveIntegerField(default=0, help_text="Technical SEO score (0-100)")
    analyzed_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = "SEO Score"
        verbose_name_plural = "SEO Scores"
    
    def __str__(self):
        return f"Score: {self.overall_score} for {self.metadata.content_object}"

class SeoIssue(models.Model):
    """
    SEO issues identified during analysis
    """
    SEVERITY_CHOICES = [
        ('critical', 'Critical'),
        ('high', 'High'),
        ('medium', 'Medium'),
        ('low', 'Low'),
        ('info', 'Info'),
    ]
    
    ISSUE_TYPE_CHOICES = [
        ('meta', 'Metadata'),
        ('content', 'Content'),
        ('keyword', 'Keyword'),
        ('technical', 'Technical'),
        ('performance', 'Performance'),
    ]
    
    score = models.ForeignKey(SeoScore, on_delete=models.CASCADE, related_name='issues')
    issue_type = models.CharField(max_length=20, choices=ISSUE_TYPE_CHOICES)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    message = models.CharField(max_length=255)
    details = models.TextField(blank=True, null=True)
    resolved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "SEO Issue"
        verbose_name_plural = "SEO Issues"
    
    def __str__(self):
        return f"{self.get_severity_display()} {self.get_issue_type_display()} issue: {self.message}"

class SitemapConfig(models.Model):
    """
    Configuration for sitemap generation
    """
    CHANGE_FREQUENCY_CHOICES = [
        ('always', 'Always'),
        ('hourly', 'Hourly'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
        ('yearly', 'Yearly'),
        ('never', 'Never'),
    ]
    
    # Content types to include
    include_blog_posts = models.BooleanField(default=True)
    include_pages = models.BooleanField(default=True)
    include_categories = models.BooleanField(default=True)
    
    # Change frequency settings
    blog_update_frequency = models.CharField(max_length=10, choices=CHANGE_FREQUENCY_CHOICES, default='weekly')
    pages_update_frequency = models.CharField(max_length=10, choices=CHANGE_FREQUENCY_CHOICES, default='monthly')
    categories_update_frequency = models.CharField(max_length=10, choices=CHANGE_FREQUENCY_CHOICES, default='monthly')
    
    # Search engine notification
    auto_ping_search_engines = models.BooleanField(default=True, 
                                               help_text="Automatically notify search engines when sitemap is updated")
    
    # Last generated
    last_generated = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Sitemap Configuration"
        verbose_name_plural = "Sitemap Configuration"
    
    def __str__(self):
        return "Sitemap Configuration"
