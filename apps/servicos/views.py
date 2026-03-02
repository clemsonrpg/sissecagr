from django.contrib import messages
from apps.pessoas.models import Propriedade
from django.shortcuts import get_object_or_404, redirect, redirect, render
from .forms import ServicoForm
from apps.pessoas.models import Pessoa
from apps.servicos.models import Servico
from django.contrib.auth.decorators import login_required

@login_required
# Create your views here.
def inserir_servico(request):
    template_name = 'servicos/form_servico.html'
    if request.method == 'POST':
        form = ServicoForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'O cadastro do serviço foi realizado com sucesso!')
            return redirect('servicos:listar_servicos')
    else:
        form = ServicoForm()
    return render(request, template_name, {'form': form})
@login_required
def listar_servicos(request):
    template_name = 'servicos/listar_servicos.html'
    servicos = Servico.objects.select_related('propriedade__pessoa').all().order_by('-data_servico', '-id')

    return render(request, template_name, {'servicos': servicos})
@login_required
def editar_servico(request, id):
    template_name = 'servicos/form_servico.html'
    servico = get_object_or_404(Servico, id=id) # Use get_object_or_404 por segurança
    form = ServicoForm(request.POST or None, request.FILES or None, instance=servico)
    
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            messages.success(request, 'Os dados foram atualizados com sucesso.')
            return redirect('servicos:listar_servicos') # Ou detalhe_pessoa
            
    context = {'form': form}
    return render(request, template_name, context)
@login_required
def excluir_servico(request, id):
    template_name = 'servicos/excluir_servico.html'
    servico = Servico.objects.get(id=id)
    context = {'servico': servico}
    if request.method == "POST":
        servico.delete()
        messages.warning(request, 'O serviço foi excluído com sucesso.')
        return redirect('servicos:listar_servicos')
    return render(request, template_name, context)
@login_required
def detalhe_servico(request, id):
    template_name = 'servicos/detalhe_servico.html'
    servico = Servico.objects.get(id=id)
    context = {'servico': servico}
    return render(request, template_name, context)
@login_required
def load_propriedades(request):
    pessoa_id = request.GET.get('pessoa_id')
    propriedades = Propriedade.objects.filter(pessoa_id=pessoa_id).order_by('nome_propriedade')
    return render(request, 'servicos/dropdown_propriedades_options.html', {'propriedades': propriedades})

from datetime import date
@login_required
def alternar_status(request, id):
    servico = get_object_or_404(Servico, id=id)
    if servico.status == "Pendente":
        servico.status = "Concluído"
        servico.data_conclusao = date.today() # Define a data de completação hoje
    else:
        servico.status = "Pendente"
        servico.data_conclusao = None # Limpa se voltar para pendente
    
    servico.save()
    return redirect('servicos:listar_servicos')
