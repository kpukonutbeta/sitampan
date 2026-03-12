from django.db import models
from django.core.validators import FileExtensionValidator

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

    class Meta:
        verbose_name_plural = "Categories"

class Document(models.Model):
    title = models.CharField(max_length=255)
    abstract = models.TextField(help_text="A brief summary of the document, searchable.", blank=True)
    file = models.FileField(upload_to='documents/', validators=[FileExtensionValidator(allowed_extensions=['pdf'])])
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='documents')
    drive_file_id = models.CharField(max_length=255, null=True, blank=True, help_text="Google Drive File ID")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
