import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khatma.settings')
django.setup()

from django.contrib.auth.models import User

# Find or create admin user
try:
    admin_user = User.objects.get(username='admin')
    print(f"Found existing admin user: {admin_user.username}")
except User.DoesNotExist:
    admin_user = User.objects.create_superuser('admin', 'admin@example.com', 'temp_password')
    print(f"Created new admin user: {admin_user.username}")

# Reset password
admin_user.set_password('Open@source7')
admin_user.save()

print("Admin password has been reset to: Open@source7")
print(f"Username: {admin_user.username}")
print(f"Email: {admin_user.email}")
print(f"Is staff: {admin_user.is_staff}")
print(f"Is superuser: {admin_user.is_superuser}")
