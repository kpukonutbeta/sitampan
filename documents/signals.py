from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Category, Document
import threading
from .drive_services import get_or_create_drive_folder, upload_document_to_drive

@receiver(post_save, sender=Category)
def category_post_save(sender, instance, created, **kwargs):
    if created and not instance.drive_folder_id:
        def sync_folder():
            get_or_create_drive_folder(instance)
        # Run in a separate thread so we don't block the request
        threading.Thread(target=sync_folder).start()

@receiver(post_save, sender=Document)
def document_post_save(sender, instance, created, **kwargs):
    # If the document has a file but hasn't been uploaded to Drive yet
    if instance.file and not instance.drive_file_id:
        def sync_file():
            upload_document_to_drive(instance)
        threading.Thread(target=sync_file).start()
