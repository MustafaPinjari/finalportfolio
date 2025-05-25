from django import forms
from .models import SeoMetadata, Keyword, SitemapConfig

class SeoMetadataForm(forms.ModelForm):
    """
    Form for editing SEO metadata
    """
    class Meta:
        model = SeoMetadata
        fields = [
            'meta_title', 
            'meta_description', 
            'meta_keywords',
            'og_title',
            'og_description',
            'og_image',
            'twitter_title',
            'twitter_description',
            'twitter_image',
            'canonical_url',
            'no_index',
            'no_follow'
        ]
        widgets = {
            'meta_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'SEO Title (50-60 characters)',
                'maxlength': 70,
                'data-seo-title': True
            }),
            'meta_description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'SEO Description (120-160 characters)',
                'rows': 3,
                'maxlength': 160,
                'data-seo-description': True
            }),
            'meta_keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Comma-separated keywords',
                'data-seo-keywords': True
            }),
            'og_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Open Graph Title',
                'maxlength': 70
            }),
            'og_description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Open Graph Description',
                'rows': 3,
                'maxlength': 200
            }),
            'twitter_title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Twitter Card Title',
                'maxlength': 70
            }),
            'twitter_description': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Twitter Card Description',
                'rows': 3,
                'maxlength': 200
            }),
            'canonical_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'Canonical URL (if different from current URL)'
            }),
            'no_index': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'no_follow': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

class KeywordForm(forms.ModelForm):
    """
    Form for adding/editing keywords
    """
    class Meta:
        model = Keyword
        fields = ['keyword', 'is_primary']
        widgets = {
            'keyword': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter keyword',
                'maxlength': 100
            }),
            'is_primary': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            })
        }

class KeywordFormSet(forms.BaseModelFormSet):
    """
    Formset for managing multiple keywords
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queryset = Keyword.objects.none()

KeywordFormSet = forms.modelformset_factory(
    Keyword,
    form=KeywordForm,
    formset=KeywordFormSet,
    extra=3,
    can_delete=True
)

class SitemapConfigForm(forms.ModelForm):
    """
    Form for sitemap configuration
    """
    class Meta:
        model = SitemapConfig
        fields = [
            'include_blog_posts',
            'include_pages',
            'include_categories',
            'auto_ping_search_engines',
            'blog_update_frequency',
            'pages_update_frequency',
            'categories_update_frequency'
        ]
        widgets = {
            'include_blog_posts': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'include_pages': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'include_categories': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'auto_ping_search_engines': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'blog_update_frequency': forms.Select(attrs={
                'class': 'form-select'
            }),
            'pages_update_frequency': forms.Select(attrs={
                'class': 'form-select'
            }),
            'categories_update_frequency': forms.Select(attrs={
                'class': 'form-select'
            })
        }
