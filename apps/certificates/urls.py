from django.urls import path
from . import views

app_name = 'certificates'

urlpatterns = [
    path('', views.certificate_list, name='list'),
    path('create/', views.certificate_create, name='create'),
    path('expiring-soon/', views.certificate_expiring_soon, name='expiring_soon'),
    path('<str:certificate_id>/', views.certificate_detail, name='detail'),
    path('<str:certificate_id>/edit/', views.certificate_edit, name='edit'),
    path('<str:certificate_id>/delete/', views.certificate_delete, name='delete'),
    path('<str:certificate_id>/download/', views.certificate_download, name='download'),
] 