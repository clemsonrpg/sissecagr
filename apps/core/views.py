from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from apps.alunos.models import Aluno
from apps.livros.models import Livro
from apps.emprestimos.models import Emprestimo

def index(request):
    total_alunos =  Aluno.objects.all().count()
    total_livros = Livro.objects.all().count()
    total_emprestimos = Emprestimo.objects.filter(status='E').count()
    context = {
        'total_alunos': total_alunos,
        'total_livros': total_livros,
        'total_emprestimos': total_emprestimos,

    }
    return render(request, 'index.html', context)