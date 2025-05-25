from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from blog.models import BlogPost

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    favorite_posts = models.ManyToManyField(BlogPost, blank=True, related_name='favorited_by')
    # Notification fields removed as requested
    date_joined = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"

# Signal to create or update user profile when user is created/updated
@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        # Check if profile exists before saving
        try:
            instance.profile.save()
        except User.profile.RelatedObjectDoesNotExist:
            # Create a profile if it doesn't exist
            UserProfile.objects.create(user=instance)
