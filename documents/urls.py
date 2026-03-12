from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('archives/', views.document_list, name='document_list'),
    path('upload/', views.document_upload, name='document_upload'),
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.category_add, name='category_add'),
    path('categories/<int:pk>/delete/', views.category_delete, name='category_delete'),
    path('<int:pk>/edit/', views.document_edit, name='document_edit'),
]
