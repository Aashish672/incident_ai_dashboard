from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from logs.models import Profile

class Command(BaseCommand):
    help = 'Create a default admin user with role=admin'

    def handle(self, *args, **kwargs):
        username = 'admin_user'
        password = 'AdminPass123'
        email = 'admin@example.com'

        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.WARNING('Admin user already exists!'))
        else:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            profile = Profile.objects.get(user=user)
            profile.role = 'admin'
            profile.save()
            self.stdout.write(self.style.SUCCESS(f'Admin user created: {username} (password: {password})'))
