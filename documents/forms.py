from django import forms
from .models import Category, Document

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'parent', 'allow_document_upload']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'parent': forms.Select(attrs={'class': 'form-select'}),
            'allow_document_upload': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def clean(self):
        cleaned_data = super().clean()
        parent = cleaned_data.get('parent')
        name = cleaned_data.get('name')

        if parent:
            # Check maximum depth
            if parent.get_depth() >= 5:
                raise forms.ValidationError("Maximum category depth is 5 levels. Cannot create more subcategories here.")
            
            # Check for self-reference
            if self.instance and parent == self.instance:
                raise forms.ValidationError("A category cannot be its own parent.")

        return cleaned_data

class DocumentForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'abstract', 'category', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'abstract': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].queryset = Category.objects.filter(allow_document_upload=True)

class DocumentEditForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'abstract']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'abstract': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
