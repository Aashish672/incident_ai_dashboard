from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # Create profile with admin role if superuser, else viewer
        role = 'admin' if instance.is_superuser else 'viewer'
        Profile.objects.create(user=instance, role=role)
    else:
        # For updates, ensure Profile exists (creates if missing)
        profile, _ = Profile.objects.get_or_create(user=instance, defaults={
            'role': 'admin' if instance.is_superuser else 'viewer'
        })
        # Optionally: update profile fields here if needed
        profile.save()
