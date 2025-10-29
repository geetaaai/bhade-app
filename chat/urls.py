from django.urls import path
from . import views

urlpatterns = [
    path('rent-status/<str:tenant_name>/', views.rent_status, name='rent_status'),
    path('add-rent/', views.add_rent, name='add_rent'),
    path('add-tenant/', views.add_tenant, name='add_tenant'),
    path('remove-tenant/<str:tenant_name>/', views.remove_tenant, name='remove_tenant'),
    path('get-tenants/', views.get_tenants, name='get_tenants'),
]