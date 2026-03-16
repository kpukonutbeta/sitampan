from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
import threading
from django.contrib import messages
from .models import Document, Category
from .forms import DocumentForm, CategoryForm, DocumentEditForm
from .drive_services import delete_drive_folder, rename_drive_file
from .utils import rename_local_file

from django.db.models import Q, Count
from django.contrib.admin.views.decorators import staff_member_required

def resolve_template(request, template_name):
    # This determines if the user is in /m/... or /d/... based on current namespace
    mode = getattr(request.resolver_match, 'namespace', 'mobile')
    # Default to mobile if for some reason namespace isn't set, although it should be
    if mode not in ['mobile', 'desktop']:
        mode = 'mobile'
    return f"documents/{mode}/{template_name}"

def dashboard(request):
    # This determines if the user is in /m/... or /d/... based on current namespace
    mode = getattr(request.resolver_match, 'namespace', 'mobile')
    
    # If desktop, use document_list view logic instead of the dashboard
    if mode == 'desktop':
        return document_list(request)

    # Fetch recent documents (Top 5)
    recent_documents = Document.objects.all().order_by('-uploaded_at')[:5]
    
    # Fetch categories with document counts
    all_categories = Category.objects.annotate(doc_count=Count('documents'))
    
    # Split into 'Main' (Root) and 'Sub' categories for the UI
    main_categories = all_categories.filter(parent=None)[:2] # Taking first 2 as 'Main'
    sub_categories = all_categories.exclude(parent=None)[:4]   # Taking next 4 as 'Sub'
    
    # In case there are no sub-categories yet, just show more roots or empty
    if not sub_categories.exists():
        sub_categories = all_categories.filter(parent=None)[2:6]

    return render(request, resolve_template(request, 'dashboard.html'), {
        'recent_documents': recent_documents,
        'main_categories': main_categories,
        'sub_categories': sub_categories,
    })

@staff_member_required
def document_list(request):
    # If in desktop mode and accessed via the document_list URL, redirect to dashboard root (since /d/ already shows archives)
    mode = getattr(request.resolver_match, 'namespace', 'mobile')
    url_name = getattr(request.resolver_match, 'url_name', '')
    if mode == 'desktop' and url_name == 'document_list':
        return redirect('desktop:dashboard')

    query = request.GET.get('q', '')
    category_id = request.GET.get('category', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')

    documents = Document.objects.all().order_by('-uploaded_at')
    
    if query:
        documents = documents.filter(
            Q(title__icontains=query) | Q(abstract__icontains=query)
        )
        
    if category_id:
        documents = documents.filter(category_id=category_id)
        
    if date_from:
        documents = documents.filter(uploaded_at__date__gte=date_from)
        
    if date_to:
        documents = documents.filter(uploaded_at__date__lte=date_to)

    categories = Category.objects.all()

    return render(request, resolve_template(request, 'document_list.html'), {
        'documents': documents,
        'categories': categories,
        'query': query,
        'category_id': category_id,
        'date_from': date_from,
        'date_to': date_to,
    })

@staff_member_required
def document_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Document uploaded successfully! It will be synced to Google Drive in the background.')
            return redirect('documents:dashboard')
    else:
        form = DocumentForm()
    return render(request, resolve_template(request, 'document_upload.html'), {'form': form})

def document_edit(request, pk):
    document = get_object_or_404(Document, pk=pk)
    old_title = document.title
    
    if request.method == 'POST':
        form = DocumentEditForm(request.POST, instance=document)
        if form.is_valid():
            updated_document = form.save(commit=False)
            new_title = updated_document.title
            
            # Save the document changes
            updated_document.save()
            
            # If title changed, rename the file in Google Drive asynchronously and locally
            if old_title != new_title:
                if document.drive_file_id:
                    def rename_file():
                        rename_drive_file(document.drive_file_id, new_title)
                    threading.Thread(target=rename_file).start()
                
                # Rename locally
                rename_local_file(document, new_title)
                
            messages.success(request, 'Document updated successfully!')
            return redirect('documents:dashboard')
    else:
        form = DocumentEditForm(instance=document)
        
    return render(request, resolve_template(request, 'document_edit.html'), {
        'form': form,
        'document': document
    })

def category_list(request):
    # Fetch all root categories
    root_categories = Category.objects.filter(parent=None)
    
    sections = []
    for root in root_categories:
        # Fetch children for each root and annotate with document counts
        children = Category.objects.filter(parent=root).annotate(doc_count=Count('documents'))
        sections.append({
            'root': root,
            'children': children,
            'child_count': children.count()
        })
        
    return render(request, resolve_template(request, 'category_grid.html'), {
        'sections': sections,
    })

def category_add(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Category created successfully! Google Drive folder is being generated.')
            return redirect('documents:category_list')
    else:
        form = CategoryForm()
    return render(request, resolve_template(request, 'category_add.html'), {'form': form})

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
    return render(request, resolve_template(request, 'category_delete.html'), context)
