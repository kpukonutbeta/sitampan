from django.db import models
from django.core.validators import FileExtensionValidator
import os

class Category(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')
    drive_folder_id = models.CharField(max_length=255, null=True, blank=True, help_text="Google Drive Folder ID")
    allow_document_upload = models.BooleanField(default=True, help_text="If checked, this category can receive documents.")

    def __str__(self):
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' -> '.join(full_path[::-1])

    def get_depth(self):
        depth = 1
        k = self.parent
        while k is not None:
            depth += 1
            k = k.parent
        return depth

    class Meta:
        verbose_name_plural = "Categories"

def document_upload_path(instance, filename):
    # Preserve extension
    ext = filename.split('.')[-1]
    # New filename from title
    new_filename = f"{instance.title}.{ext}"
    
    # Build category hierarchy path
    path_components = []
    curr = instance.category
    while curr:
        path_components.insert(0, curr.name)
        curr = curr.parent
        
    return os.path.join('documents', *path_components, new_filename)

class Document(models.Model):
    title = models.CharField(max_length=255)
    abstract = models.TextField(help_text="A brief summary of the document, searchable.", blank=True)
    file = models.FileField(upload_to=document_upload_path, validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='documents')
    drive_file_id = models.CharField(max_length=255, null=True, blank=True, help_text="Google Drive File ID")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
