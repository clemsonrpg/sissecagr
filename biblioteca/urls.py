from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('', include("apps.core.urls")),
    path('alunos/', include('apps.alunos.urls', namespace='alunos')),
    path('livros/', include('apps.livros.urls', namespace='livros')),
    path('emprestimos/', include('apps.emprestimos.urls', namespace='emprestimos')),
    path('admin/', admin.site.urls),
]
