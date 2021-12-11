from django.urls import path
from .views import index, add_firewall, edit_firewall, delete_firewall

urlpatterns = [
    path('', index, name='firewall_index'),
    path('add/', add_firewall, name='firewall_add'),
    path('<int:firewall_id>/edit/', edit_firewall, name='firewall_edit'),
    path('<int:firewall_id>/delete/', delete_firewall, name='firewall_delete'),
]