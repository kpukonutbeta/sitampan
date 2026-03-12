import os
from django.conf import settings

def rename_local_file(document, new_title):
    if not document.file:
        return
    
    try:
        old_path = document.file.path
        if not os.path.exists(old_path):
            return
        
        # Get directory and old filename
        dir_name = os.path.dirname(old_path)
        old_filename = os.path.basename(old_path)
        
        # Get extension
        ext = old_filename.split('.')[-1]
        new_filename = f"{new_title}.{ext}"
        
        new_path = os.path.join(dir_name, new_filename)
        
        if old_path != new_path:
            # Ensure the new filename doesn't already exist to avoid overwriting or errors
            # If it exists, we might want to append something, but for now let's just rename
            os.rename(old_path, new_path)
            
            # Update the file field name (relative to MEDIA_ROOT)
            rel_path = os.path.relpath(new_path, settings.MEDIA_ROOT)
            document.file.name = rel_path
            document.save(update_fields=['file'])
    except Exception as e:
        # Log error or handle gracefully
        print(f"Error renaming local file: {e}")
