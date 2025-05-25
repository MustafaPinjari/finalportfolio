from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from .models import UserProfile
from blog.models import BlogPost, Category, Comment
from taggit.forms import TagWidget

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        
        # Add Tailwind CSS classes to form fields
        for fieldname in self.fields:
            self.fields[fieldname].widget.attrs['class'] = 'w-full rounded-lg border border-gray-400 bg-slate-100 px-3 py-4 focus:outline-none dark:border-lightHover dark:bg-[#19002c]'

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super(CustomAuthenticationForm, self).__init__(*args, **kwargs)
        
        # Add Tailwind CSS classes to form fields
        for fieldname in self.fields:
            self.fields[fieldname].widget.attrs['class'] = 'w-full rounded-lg border border-gray-400 bg-slate-100 px-3 py-4 focus:outline-none dark:border-lightHover dark:bg-[#19002c]'
            
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('profile_picture', 'bio')  # Notification fields removed as requested
        
    def __init__(self, *args, **kwargs):
        super(UserProfileForm, self).__init__(*args, **kwargs)
        
        # Add Tailwind CSS classes to form fields
        for fieldname in self.fields:
            if isinstance(self.fields[fieldname].widget, forms.CheckboxInput):
                self.fields[fieldname].widget.attrs['class'] = 'h-5 w-5 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 dark:border-lightHover'
            else:
                self.fields[fieldname].widget.attrs['class'] = 'w-full rounded-lg border border-gray-400 bg-slate-100 px-3 py-4 focus:outline-none dark:border-lightHover dark:bg-[#19002c]'

# New forms for admin panel
class UserCreateForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    is_staff = forms.BooleanField(required=False, label='Staff status', help_text='Designates whether the user can log into the admin site.')
    is_superuser = forms.BooleanField(required=False, label='Superuser status', help_text='Designates that this user has all permissions without explicitly assigning them.')
    is_active = forms.BooleanField(required=False, initial=True, label='Active', help_text='Designates whether this user should be treated as active.')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2', 'is_active', 'is_staff', 'is_superuser')
        
    def __init__(self, *args, **kwargs):
        super(UserCreateForm, self).__init__(*args, **kwargs)
        
        # Add Tailwind CSS classes to form fields
        for fieldname in self.fields:
            if isinstance(self.fields[fieldname].widget, forms.CheckboxInput):
                self.fields[fieldname].widget.attrs['class'] = 'h-5 w-5 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 dark:border-lightHover'
            else:
                self.fields[fieldname].widget.attrs['class'] = 'w-full rounded-lg border border-gray-400 bg-gray-50 px-3 py-2 text-gray-900 focus:outline-none dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:focus:border-purple-500'

class UserEditForm(forms.ModelForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    is_staff = forms.BooleanField(required=False, label='Staff status', help_text='Designates whether the user can log into the admin site.')
    is_superuser = forms.BooleanField(required=False, label='Superuser status', help_text='Designates that this user has all permissions without explicitly assigning them.')
    is_active = forms.BooleanField(required=False, label='Active', help_text='Designates whether this user should be treated as active.')
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'is_superuser')
        
    def __init__(self, *args, **kwargs):
        super(UserEditForm, self).__init__(*args, **kwargs)
        
        # Add Tailwind CSS classes to form fields
        for fieldname in self.fields:
            if isinstance(self.fields[fieldname].widget, forms.CheckboxInput):
                self.fields[fieldname].widget.attrs['class'] = 'h-5 w-5 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 dark:border-lightHover'
            else:
                self.fields[fieldname].widget.attrs['class'] = 'w-full rounded-lg border border-gray-400 bg-gray-50 px-3 py-2 text-gray-900 focus:outline-none dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:focus:border-purple-500'

class BlogPostForm(forms.ModelForm):
    title = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'placeholder': 'Enter post title'}))
    content = forms.CharField(widget=forms.Textarea(attrs={'rows': 12, 'placeholder': 'Write your post content here...'}))
    excerpt = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter a short excerpt (optional)'}))
    is_published = forms.BooleanField(required=False, initial=True, label='Published', help_text='Uncheck to save as draft')
    allow_comments = forms.BooleanField(required=False, initial=True, label='Allow Comments')
    featured_post = forms.BooleanField(required=False, label='Featured Post', help_text='Featured posts will be displayed prominently on the home page')
    
    class Meta:
        model = BlogPost
        fields = ('title', 'slug', 'content', 'excerpt', 'image', 
                  'category', 'tags', 'is_published', 'allow_comments', 'featured_post')
        widgets = {
            'slug': forms.TextInput(attrs={'placeholder': 'Leave blank to auto-generate from title'}),
            'tags': TagWidget(attrs={'placeholder': 'Add comma-separated tags'}),
        }
        
    def __init__(self, *args, **kwargs):
        super(BlogPostForm, self).__init__(*args, **kwargs)
        
        # Make slug field optional
        self.fields['slug'].required = False
        
        # Add Tailwind CSS classes to form fields
        for fieldname in self.fields:
            if isinstance(self.fields[fieldname].widget, forms.CheckboxInput):
                self.fields[fieldname].widget.attrs['class'] = 'h-5 w-5 rounded border-gray-300 text-indigo-600 focus:ring-indigo-500 dark:border-lightHover'
            elif isinstance(self.fields[fieldname].widget, forms.SelectMultiple):
                self.fields[fieldname].widget.attrs['class'] = 'w-full rounded-lg border border-gray-400 bg-gray-50 px-3 py-2 text-gray-900 focus:outline-none dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:focus:border-purple-500'
            elif isinstance(self.fields[fieldname].widget, TagWidget):
                self.fields[fieldname].widget.attrs['class'] = 'w-full rounded-lg border border-gray-400 bg-gray-50 px-3 py-2 text-gray-900 focus:outline-none dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:focus:border-purple-500'
            else:
                self.fields[fieldname].widget.attrs['class'] = 'w-full rounded-lg border border-gray-400 bg-gray-50 px-3 py-2 text-gray-900 focus:outline-none dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:focus:border-purple-500'
    
    def clean_slug(self):
        """Auto-generate slug if not provided"""
        slug = self.cleaned_data.get('slug')
        title = self.cleaned_data.get('title')
        
        if not slug and title:
            from django.utils.text import slugify
            slug = slugify(title)
            
            # Check if slug already exists
            count = 0
            original_slug = slug
            while BlogPost.objects.filter(slug=slug).exclude(id=self.instance.id if self.instance else None).exists():
                count += 1
                slug = f"{original_slug}-{count}"
                
        return slug

class CategoryForm(forms.ModelForm):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'placeholder': 'Category name'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 3, 'placeholder': 'Description (optional)'}))
    
    class Meta:
        model = Category
        fields = ('name', 'slug', 'description')
        widgets = {
            'slug': forms.TextInput(attrs={'placeholder': 'Leave blank to auto-generate from name'}),
        }
        
    def __init__(self, *args, **kwargs):
        super(CategoryForm, self).__init__(*args, **kwargs)
        
        # Make slug field optional
        self.fields['slug'].required = False
        
        # Add Tailwind CSS classes to form fields
        for fieldname in self.fields:
            self.fields[fieldname].widget.attrs['class'] = 'w-full rounded-lg border border-gray-400 bg-gray-50 px-3 py-2 text-gray-900 focus:outline-none dark:border-gray-600 dark:bg-gray-700 dark:text-white dark:focus:border-purple-500'
    
    def clean_slug(self):
        """Auto-generate slug if not provided"""
        slug = self.cleaned_data.get('slug')
        name = self.cleaned_data.get('name')
        
        if not slug and name:
            from django.utils.text import slugify
            slug = slugify(name)
            
            # Check if slug already exists
            count = 0
            original_slug = slug
            while Category.objects.filter(slug=slug).exclude(id=self.instance.id if self.instance else None).exists():
                count += 1
                slug = f"{original_slug}-{count}"
                
        return slug
