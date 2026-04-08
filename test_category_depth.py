
import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sitampan.settings')
django.setup()

from unittest.mock import patch
from documents.models import Category
from documents.forms import CategoryForm

@patch('documents.drive_services.get_drive_service', return_value=None)
def test_category_depth(mock_service):
    print("Testing category depth validation (mocking Drive)...")
    
    # Clear existing test categories if any
    Category.objects.filter(name__startswith="TestLevel").delete()
    
    # Create 5 levels
    current_parent = None
    for i in range(1, 6):
        name = f"TestLevel{i}"
        cat = Category.objects.create(name=name, parent=current_parent)
        print(f"Created {name} at depth {cat.get_depth()}")
        current_parent = cat
        
    # Attempt to create 6th level via form
    print("\nAttempting to create 6th level via CategoryForm...")
    form_data = {
        'name': 'TestLevel6',
        'parent': current_parent.id,
        'allow_document_upload': True
    }
    form = CategoryForm(data=form_data)
    
    if not form.is_valid():
        print(f"Validation failed as expected: {form.errors.as_text()}")
        if "Maximum category depth is 5 levels" in form.errors.as_text():
            print("SUCCESS: Depth validation is working correctly.")
        else:
            print("FAILURE: Unexpected error message.")
    else:
        print("FAILURE: Form was valid but should have failed depth limit.")

if __name__ == "__main__":
    test_category_depth()
