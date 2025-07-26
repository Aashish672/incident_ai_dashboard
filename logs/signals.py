from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Profile

@receiver(post_save,sender=User)
def create_or_update_user_profile(sender,instance,created,**kwargs):
    if created:
        # If superuser, assign admin role
        if instance.is_superuser:
            Profile.objects.create(user=instance, role='admin')
        else:
            Profile.objects.create(user=instance,role='viewer')
    else:
        instance.profile.save()