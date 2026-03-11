from django.contrib import admin
from .models import Category, Document

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'drive_folder_id')
    search_fields = ('name',)

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'uploaded_at', 'drive_file_id')
    search_fields = ('title',)
    list_filter = ('category', 'uploaded_at')
