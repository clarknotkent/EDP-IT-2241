from django.urls import path
from . import views

urlpatterns = [
    path('students', views.students, name='students.index'),
    path('add', views.add, name='add.index'),
    path('update/<int:pk>/', views.update, name='update.index'),
]
