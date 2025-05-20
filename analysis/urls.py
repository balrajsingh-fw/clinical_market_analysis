from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('sales-analysis/', views.sales_analysis, name='sales_analysis'),
    path('drug-analysis/', views.drug_analysis, name='drug_analysis')
]