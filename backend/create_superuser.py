import os
import django

# Set up Django environment
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Grab details from environment variables
username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

if not all([username, email, password]):
    print("⚠️ Superuser environment variables are missing. Skipping initialization.")
else:
    # Check if the user already exists to prevent crashes on redeployment
    if not User.objects.filter(username=username).exists():
        print(f"🚀 Creating superuser: {username}...")
        User.objects.create_superuser(username=username, email=email, password=password)
        print("✅ Superuser created successfully!")
    else:
        print(f"ℹ️ Superuser '{username}' already exists. Skipping.")