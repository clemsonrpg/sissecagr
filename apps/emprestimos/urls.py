from django.urls import path
from apps.emprestimos import views

app_name = 'apps.emprestimos'

urlpatterns = [
    path('inserir_emprestimo', views.inserir_emprestimo, name='inserir_emprestimo'),
    path('listar_emprestimos', views.listar_emprestimos, name='listar_emprestimos'),
    path('editar_emprestimo/<int:id>', views.editar_emprestimo, name='editar_emprestimo'),
]