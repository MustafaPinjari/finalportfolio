from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import BlogPost

class BlogSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.9

    def items(self):
        return BlogPost.objects.all()

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse('blog:blog_detail', args=[obj.slug])

class StaticSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.8

    def items(self):
        return ['home', 'blog:blog_list']

    def location(self, item):
        return reverse(item)