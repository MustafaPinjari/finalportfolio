from django.contrib import admin
from django.contrib.auth.models import User
from .models import Category, BlogPost, Comment, ContactMessage, Project, ProjectScreenshot

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'description')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    ordering = ('name',)

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'created_at', 'views_count')
    list_filter = ('category', 'created_at', 'author')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ['author']  # Keep this for author selection
    # Remove filter_horizontal as it's not compatible with taggit

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "author":
            kwargs["queryset"] = User.objects.filter(is_staff=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'post', 'created_at')
    list_filter = ('created_at', 'author')
    search_fields = ('content', 'author__username')

from .models import ContactMessage

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'created_at')
    search_fields = ('name', 'email', 'message')
    readonly_fields = ('created_at',)

class ProjectScreenshotInline(admin.TabularInline):
    model = ProjectScreenshot
    extra = 1
    fields = ('image', 'title', 'description', 'size', 'order')

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'featured', 'created_at')
    list_filter = ('category', 'featured', 'created_at')
    search_fields = ('title', 'description', 'content')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [ProjectScreenshotInline]

@admin.register(ProjectScreenshot)
class ProjectScreenshotAdmin(admin.ModelAdmin):
    list_display = ('project', 'title', 'size', 'order')
    list_filter = ('project', 'size')
    search_fields = ('title', 'description', 'project__title')
    ordering = ('project', 'order')
