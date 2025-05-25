from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .forms import CustomUserCreationForm, UserProfileForm, CustomAuthenticationForm
from .models import UserProfile
from blog.models import BlogPost
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings

def login_view(request):
    """Custom login view that directly renders the login template"""
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                # Redirect staff users to the custom admin dashboard
                if user.is_staff:
                    return redirect('custom_admin')
                return redirect('profile')
            else:
                messages.error(request,"Invalid username or password.")
        else:
            messages.error(request,"Invalid username or password.")
    else:
        form = CustomAuthenticationForm()
    return render(request, 'users/login.html', {"form": form})

def logout_view(request):
    """Custom logout view with redirect"""
    logout(request)
    messages.info(request, "You have successfully logged out.") 
    return redirect('/')

def register_view(request):
    """Custom registration view"""
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Account created for {username}!')
                return redirect('profile')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

@login_required
def profile_view(request):
    if request.method == 'POST':
        user_form = CustomUserCreationForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated!')
            return redirect('profile')
    else:
        user_form = CustomUserCreationForm(instance=request.user)
        profile_form = UserProfileForm(instance=request.user.profile)
    
    # Get user stats
    favorite_posts = request.user.profile.favorite_posts.all()
    favorite_count = favorite_posts.count()
    
    # Get comment count - assuming you have a Comment model related to user
    from blog.models import Comment
    comment_count = Comment.objects.filter(author=request.user).count()
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
        'favorite_posts': favorite_posts,
        'favorite_count': favorite_count,
        'comment_count': comment_count,
        'active_tab': 'profile'
    }
    return render(request, 'users/profile_new.html', context)

@login_required
def toggle_favorite_post(request, post_id):
    """Add or remove a post from user's favorites"""
    if request.method == 'POST':
        post = get_object_or_404(BlogPost, id=post_id)
        user_profile = request.user.profile
        
        # Toggle favorite status
        if post in user_profile.favorite_posts.all():
            user_profile.favorite_posts.remove(post)
            is_favorite = False
        else:
            user_profile.favorite_posts.add(post)
            is_favorite = True
            
        return JsonResponse({'status': 'success', 'is_favorite': is_favorite})
    return JsonResponse({'status': 'error'}, status=400)

@login_required
def favorite_posts_view(request):
    """Display all favorite posts of the user"""
    favorite_posts = request.user.profile.favorite_posts.all()
    context = {
        'favorite_posts': favorite_posts,
        'active_tab': 'favorites'
    }
    return render(request, 'users/favorite_posts_new.html', context)

@login_required
def user_comments_view(request):
    """Display all comments made by the user"""
    from blog.models import Comment
    user_comments = Comment.objects.filter(author=request.user).select_related('post').order_by('-date_posted')
    context = {
        'user_comments': user_comments,
        'active_tab': 'comments'
    }
    return render(request, 'users/user_comments.html', context)

# Notification system functions removed as requested
