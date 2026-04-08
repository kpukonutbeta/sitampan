import os
import django
import sys

# Set up Django environment
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sitampan.settings')
django.setup()

from django.contrib.sites.models import Site

def update_domain(new_domain):
    try:
        site = Site.objects.get(id=1)
        old_domain = site.domain
        site.domain = new_domain
        site.name = f"SITAMPAN ({new_domain})"
        site.save()
        print(f"Successfully updated Site domain from '{old_domain}' to '{new_domain}'")
    except Site.DoesNotExist:
        Site.objects.create(id=1, domain=new_domain, name=f"SITAMPAN ({new_domain})")
        print(f"Created new Site with domain '{new_domain}'")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/update_site_domain.py <new_domain>")
        sys.exit(1)
    
    update_domain(sys.argv[1])
