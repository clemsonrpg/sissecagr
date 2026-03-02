from django.urls import path
from . import views

app_name = 'core' # Isso é obrigatório para usar core:nome

urlpatterns = [
    path('', views.index, name='index'),
    path('relatorios/', views.relatorios, name='relatorios'), # Verifique se tem o 's' aqui
    path('relatorios/excel/', views.relatorio_excel, name='relatorio_excel'),
    
]