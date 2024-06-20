from django.urls import path

from . import views

app_name = 'students'

urlpatterns = [
    path('', views.student_list, name='list'),
    path('add/', views.student_add, name='add'),
    path('export.csv', views.student_export, name='export'),
    path('bulk-delete/', views.student_bulk_delete, name='bulk_delete'),
    path('<int:pk>/', views.student_detail, name='detail'),
    path('<int:pk>/edit/', views.student_update, name='update'),
    path('<int:pk>/delete/', views.student_delete, name='delete'),
]
