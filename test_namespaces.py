import django
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "sitampan.settings")
django.setup()
from django.urls import reverse
# Just a quick print verify
print("Django loaded")
