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
                raise forms.ValidationError("Kedalaman kategori maksimum adalah 5 tingkat. Tidak dapat membuat subkategori lebih lanjut di sini.")
            
            # Check for self-reference
            if self.instance and parent == self.instance:
                raise forms.ValidationError("Kategori tidak dapat menjadi induk bagi dirinya sendiri.")

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

    lock_on_upload = forms.BooleanField(required=False, label="Kunci Dokumen", widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    pdf_password = forms.CharField(required=False, label="Password PDF", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Biarkan kosong untuk menggunakan password default'}))

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

class SiteSettingsForm(forms.ModelForm):
    class Meta:
        from .models import SiteSettings
        model = SiteSettings
        fields = ['theme_color', 'default_pdf_password']
        widgets = {
            'theme_color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control form-control-color', 'title': 'Pilih Warna Tema'}),
            'default_pdf_password': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password default untuk mengunci PDF'}),
        }

    confirm_password = forms.CharField(required=False, label="Konfirmasi Password", widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Ketik ulang password default'}))

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('default_pdf_password')
        confirm = cleaned_data.get('confirm_password')

        if password and password != confirm:
            self.add_error('confirm_password', "Password konfirmasi tidak cocok.")
        
        return cleaned_data
