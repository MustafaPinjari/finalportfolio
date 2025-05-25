from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import User
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from collections import Counter
from taggit.managers import TaggableManager  # Add this import
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)  # Remove choices constraint
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    content = models.TextField()
    slug = models.SlugField(unique=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(upload_to='blog_images/', null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='posts')
    tags = TaggableManager()
    views_count = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True, help_text='Whether this post is publicly visible')
    
    def increment_views(self):
        self.views_count += 1
        self.save()
    
    def analyze_content_for_category(self):
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')

        # Combine title and content for analysis
        text = f"{self.title} {self.content}"
        
        # Tokenize and clean text
        tokens = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word.isalnum() and word not in stop_words]

        # Enhanced category keywords with more specific terms
        category_keywords = {
            'Technology': ['technology', 'software', 'programming', 'code', 'computer', 'ai', 'robot', 'iot', 'automation',
                         'sensor', 'module', 'system', 'navigation', 'lcd', 'display', 'interface', 'machine learning',
                         'artificial intelligence', 'smart', 'device', 'electronic', 'digital', 'hardware'],
            'Innovation': ['innovation', 'revolutionising', 'future', 'advancement', 'modern', 'smart', 'automated',
                         'efficiency', 'solution', 'enhancement', 'improvement', 'development'],
            'Business': ['business', 'commercial', 'service', 'customer', 'operation', 'cost', 'industry', 'sector',
                        'market', 'enterprise', 'startup', 'solution', 'management'],
            'Engineering': ['engineering', 'development', 'technical', 'system', 'design', 'implementation',
                          'integration', 'architecture', 'framework', 'infrastructure']
        }

        # Improved scoring system with weighted keywords
        category_scores = {}
        for category, keywords in category_keywords.items():
            score = 0
            for token in tokens:
                # Give higher weight to title matches
                if token in self.title.lower():
                    score += 2
                # Regular content matches
                if token in keywords:
                    score += 1
            category_scores[category] = score

        # Get category with highest score, require minimum score
        if category_scores:
            best_category = max(category_scores.items(), key=lambda x: x[1])
            if best_category[1] > 0:  # Ensure we have at least some matches
                category, _ = Category.objects.get_or_create(
                    name=best_category[0],
                    defaults={'slug': slugify(best_category[0])}
                )
                return category
        return None

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        
        # Auto-assign category if not set
        if not self.category:
            self.category = self.analyze_content_for_category()
            
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class Comment(models.Model):
    post = models.ForeignKey(BlogPost, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='replies')
    likes = models.ManyToManyField(User, related_name='comment_likes', blank=True)
    
    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.author} on {self.post}'

    @property
    def is_reply(self):
        return self.parent is not None

    def get_likes_count(self):
        return self.likes.count()


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.created_at.strftime('%Y-%m-%d')}"

    class Meta:
        ordering = ['-created_at']


class PageView(models.Model):
    path = models.CharField(max_length=255)
    ip_address = models.GenericIPAddressField()
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL)
    timestamp = models.DateTimeField(default=timezone.now)
    session_key = models.CharField(max_length=40, null=True, blank=True)

class UserActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    action_type = models.CharField(max_length=50)  # login, register, comment, etc.
    timestamp = models.DateTimeField(default=timezone.now)

class AnalyticsData(models.Model):
    date = models.DateField(unique=True)
    page_views = models.IntegerField(default=0)
    unique_visitors = models.IntegerField(default=0)
    new_users = models.IntegerField(default=0)
    active_users = models.IntegerField(default=0)
    total_comments = models.IntegerField(default=0)


class Project(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField()
    content = models.TextField(blank=True, help_text="Detailed project information")
    features = models.TextField(blank=True, help_text="Comma-separated list of project features")
    image = models.ImageField(upload_to='project_images/')
    technologies = models.CharField(max_length=255, help_text="Comma-separated list of technologies used")
    github_link = models.URLField(blank=True, null=True)
    live_link = models.URLField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='projects')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    featured = models.BooleanField(default=False)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Check for existing slugs and add a number suffix if needed
            original_slug = self.slug
            counter = 1
            while Project.objects.filter(slug=self.slug).exists():
                self.slug = f"{original_slug}-{counter}"
                counter += 1
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    @property
    def technology_list(self):
        if not self.technologies:
            return []
        return [tech.strip() for tech in self.technologies.split(',')]
    
    @property
    def features_list(self):
        if not self.features:
            return []
        return [feature.strip() for feature in self.features.split(',')]
        
    @property
    def ui_screenshot_count(self):
        return self.screenshots.count()


class ProjectScreenshot(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='screenshots')
    image = models.ImageField(upload_to='project_screenshots/')
    title = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    size = models.CharField(max_length=20, choices=[
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
        ('wide', 'Wide'),
        ('tall', 'Tall')
    ], default='medium', help_text='Size in the bento grid layout')
    
    class Meta:
        ordering = ['order']
        verbose_name = 'Project Screenshot'
        verbose_name_plural = 'Project Screenshots'
    
    def __str__(self):
        return f"{self.project.title} - {self.title or f'Screenshot {self.order + 1}'}"
