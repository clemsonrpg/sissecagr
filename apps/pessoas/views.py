from django.contrib import messages
from urllib3 import request
from apps.servicos.models import Servico
from .forms import PessoaForm, PropriedadeFormSet
from django.shortcuts import render, redirect, get_object_or_404
from .models import Pessoa
from django.contrib.auth.decorators import login_required
@login_required
def inserir_pessoa(request):
    template_name = 'pessoas/form_pessoa.html'
    if request.method == 'POST':
        form = PessoaForm(request.POST or None, request.FILES)
        if form.is_valid():
            pessoa = form.save()
            messages.success(request, 'O cadastro da pessoa foi realizado com sucesso!')
            return redirect('pessoas:inserir_propriedade', pessoa.id)
    form = PessoaForm()
    context = {'form': form}
    return render(request, template_name, context)

from django.db.models import Prefetch
@login_required
def listar_pessoas(request):
    template_name = 'pessoas/listar_pessoas.html'

    pessoas = Pessoa.objects.order_by('nome').prefetch_related(
        Prefetch(
            'propriedades__servicos',
            queryset=Servico.objects.order_by('-id'),
            to_attr='servicos_ordenados'
        )
    ).order_by('-id')

    for pessoa in pessoas:
        ultimo = None

        for prop in pessoa.propriedades.all():
            if hasattr(prop, 'servicos_ordenados') and prop.servicos_ordenados:
                if not ultimo or prop.servicos_ordenados[0].id > ultimo.id:
                    ultimo = prop.servicos_ordenados[0]

        pessoa.ultimo_servico = ultimo

    context = {'pessoas': pessoas}
    return render(request, template_name, context)
@login_required
def editar_pessoa(request, id):
    template_name = 'pessoas/form_pessoa.html'
    pessoa = get_object_or_404(Pessoa, id=id)
    form = PessoaForm(request.POST or None, request.FILES or None, instance=pessoa)
    context = {'form': form}
    if form.is_valid():
        form.save()
        messages.success(request, 'Os dados foram atualizados com sucesso.')
        return redirect('pessoas:listar_pessoas')
    return render(request, template_name, context)
@login_required
def excluir_pessoa(request, id):
    
    template_name = 'pessoas/excluir_pessoa.html'


    pessoa = Pessoa.objects.get(id=id)
    context = {'pessoa': pessoa}
    if request.method == "POST":
        pessoa.delete()
        messages.warning(request, 'A pessoa foi excluída com sucesso.')
        return redirect('pessoas:listar_pessoas')
    return render(request, template_name, context)

@login_required
def detalhe_pessoa(request, id):
    template_name = 'pessoas/detalhe_pessoa.html'
    pessoa = get_object_or_404(Pessoa, id=id)
    propriedades = pessoa.propriedades.prefetch_related('servicos')
    servicos = Servico.objects.filter(propriedade__pessoa=pessoa)
    context = {'pessoa': pessoa, 'propriedades': propriedades, 'servicos': servicos}
    return render(request, template_name, context)


from .forms import PropriedadeForm
@login_required
def inserir_propriedade(request, pessoa_id):
    template_name = 'pessoas/form_propriedade.html'
    pessoa = get_object_or_404(Pessoa, id=pessoa_id)

    if request.method == 'POST':
        formset = PropriedadeFormSet(request.POST, instance=pessoa)
        if formset.is_valid():
            formset.save()
            messages.success(request, 'Propriedades cadastradas com sucesso!')
            return redirect('pessoas:detalhe_pessoa', pessoa.id)
    else:
        formset = PropriedadeFormSet(instance=pessoa)

    context = {
        'pessoa': pessoa,
        'formset': formset
    }
    return render(request, template_name, context)