import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khatma.settings')
django.setup()

# Import Django models
from django.contrib.auth.models import User

# Define admin credentials
username = 'admin123'
email = 'admin123@example.com'
password = 'admin123'

# Delete existing user if it exists
if User.objects.filter(username=username).exists():
    User.objects.filter(username=username).delete()
    print(f"Deleted existing user: {username}")

# Create new superuser
User.objects.create_superuser(username=username, email=email, password=password)
print(f"Created new superuser:")
print(f"Username: {username}")
print(f"Password: {password}")
print(f"Email: {email}")
print("\nYou can now log in to the admin panel at http://localhost:8000/admin/")
