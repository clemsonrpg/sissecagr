from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404

from apps.emprestimos.forms import EmprestimoForm
from apps.emprestimos.models import Emprestimo


def inserir_emprestimo(request):
    template_name = 'emprestimos/form_emprestimo.html'
    if request.method == 'POST':
        form = EmprestimoForm(request.POST or None, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'O cadastro de empréstimo foi realizado com sucesso!')
        return redirect('emprestimos:listar_emprestimos')
    form = EmprestimoForm()
    context = {'form': form}
    return render(request, template_name, context)


def listar_emprestimos(request):
    template_name = 'emprestimos/listar_emprestimos.html'
    emprestimos = Emprestimo.objects.all()
    context = {'relacao_emprestimos': emprestimos}
    return render(request, template_name, context)

def editar_emprestimo(request, id):
    template_name = 'emprestimos/form_emprestimo.html'
    emprestimo = get_object_or_404(Emprestimo, pk=id)
    form = EmprestimoForm(request.POST or None, request.FILES or None, instance=emprestimo)
    context = {'form': form}
    if form.is_valid():
        form.save()
        messages.success(request, 'Os dados foram atualizados com sucesso.')
        return redirect('emprestimos:listar_emprestimos')
    return render(request, template_name, context)