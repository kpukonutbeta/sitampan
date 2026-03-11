from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import threading
from django.contrib import messages
from .models import Document, Category
from .forms import DocumentForm, CategoryForm
from .drive_services import delete_drive_folder

def document_list(request):
    documents = Document.objects.all().order_by('-uploaded_at')
    return render(request, 'documents/document_list.html', {'documents': documents})

def document_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Document uploaded successfully! It will be synced to Google Drive in the background.')
            return redirect('documents:document_list')
    else:
        form = DocumentForm()
    return render(request, 'documents/document_upload.html', {'form': form})

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'documents/category_list.html', {'categories': categories})

def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully! Google Drive folder is being generated.')
            return redirect('documents:category_list')
    else:
        form = CategoryForm()
    return render(request, 'documents/category_add.html', {'form': form})

def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    
    # Find all documents in this category and its subcategories
    def get_all_subcategories(cat):
        subcats = list(cat.children.all())
        for child in cat.children.all():
            subcats.extend(get_all_subcategories(child))
        return subcats
        
    categories_to_delete = [category] + get_all_subcategories(category)
    affected_documents = Document.objects.filter(category__in=categories_to_delete)
    
    if request.method == 'POST':
        # If there are affected documents, check if a target category was selected
        if affected_documents.exists():
            target_category_id = request.POST.get('target_category')
            if not target_category_id:
                messages.error(request, 'You must select a target category for existing documents.')
                return redirect('documents:category_delete', pk=pk)
                
            target_category = get_object_or_404(Category, pk=target_category_id)
            if target_category in categories_to_delete:
                messages.error(request, 'Target category cannot be the one being deleted or its subcategories.')
                return redirect('documents:category_delete', pk=pk)
                
            # Move documents to the new category
            affected_documents.update(category=target_category)
            messages.info(request, f'Moved {affected_documents.count()} documents to {target_category.name}. Note: Physical files in Google Drive must be moved manually if needed.')
            
        drive_folder_id = category.drive_folder_id
        
        # Delete the category (cascades to subcategories)
        category.delete()
        
        # Trash the folder in Google Drive asynchronously
        if drive_folder_id:
            def trash_folder():
                delete_drive_folder(drive_folder_id)
            threading.Thread(target=trash_folder).start()
            
        messages.success(request, 'Category deleted and Google Drive folder moved to trash.')
        return redirect('documents:category_list')

    # Available categories for reassignment (excluding the one being deleted and its children)
    available_categories = Category.objects.filter(allow_document_upload=True).exclude(id__in=[c.id for c in categories_to_delete])
    
    
    context = {
        'category': category,
        'affected_documents_count': affected_documents.count(),
        'available_categories': available_categories,
    }
    return render(request, 'documents/category_delete.html', context)
