from django.shortcuts import render
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Count, Q, Prefetch
from django.db.models.functions import TruncMonth
import json
from openpyxl import Workbook
from openpyxl.styles import Font, Alignment
from django.contrib.auth.decorators import login_required

from apps.servicos.models import Servico
from apps.pessoas.models import Pessoa, Propriedade

@login_required
def index(request):
    hoje = timezone.localdate()

    # OTIMIZAÇÃO: Buscamos os aniversariantes já trazendo o último serviço de cada um
    aniversariantes_queryset = Pessoa.objects.filter(
        data_nascimento__month=hoje.month,
        data_nascimento__day=hoje.day
    ).prefetch_related(
        Prefetch(
            'servicos',
            queryset=Servico.objects.order_by('-data_servico', '-id'),
            to_attr='ultimos_servicos'
        )
    )

    lista_aniversariantes = []
    for p in aniversariantes_queryset:
        idade = hoje.year - p.data_nascimento.year - (
            (hoje.month, hoje.day) < (p.data_nascimento.month, p.data_nascimento.day)
        )
        
        ultimo_servico = p.ultimos_servicos[0].nome_servico if p.ultimos_servicos else "Nenhum serviço"

        lista_aniversariantes.append({
            "nome": p.nome,
            "email": p.email or "Não informado",
            "telefone": p.telefone or "Não informado",
            "idade": idade,
            "servico": ultimo_servico
        })

    context = {
        'total_pessoas': Pessoa.objects.count(),
        'total_servicos': Servico.objects.count(),
        'lista_aniversariantes': lista_aniversariantes,
    }
    return render(request, 'index.html', context)

@login_required
def relatorios(request):
    template_name = 'core/relatorios.html'
    hoje = timezone.localdate()
    
    # Captura dos filtros do GET
    localidade_filtro = request.GET.get('localidade')
    servico_tipo_filtro = request.GET.get('servico_tipo')
    
    # 1. Base de dados (QuerySet inicial)
    servicos_qs = Servico.objects.all()
    
    # 2. Aplicação de Filtros Cumulativos
    if localidade_filtro:
        servicos_qs = servicos_qs.filter(propriedade__localidade=localidade_filtro)
        dict_choices = dict(Propriedade._meta.get_field('localidade').choices)
        localidade_nome_exibicao = dict_choices.get(localidade_filtro)
    else:
        localidade_nome_exibicao = "Geral"

    if servico_tipo_filtro:
        servicos_qs = servicos_qs.filter(nome_servico=servico_tipo_filtro)

    # 3. Listas para o Template (Realizados e Pendentes baseados no filtro)
    # Esta lista atende ao seu pedido: mostra tudo, só regiao, só tipo ou ambos.
    servicos_realizados_lista = servicos_qs.select_related('propriedade__pessoa', 'propriedade').order_by('-data_servico')
    
    servicos_pendentes = servicos_qs.filter(status="Pendente")

    # 4. Totais para os Cards
    total_mes = servicos_qs.exclude(status="Pendente").filter(
        data_servico__month=hoje.month, 
        data_servico__year=hoje.year
    ).count()
    
    total_pendentes = servicos_pendentes.count()
    total_servicos_filtrados = servicos_qs.count()

    # 5. Ranking (Top 5 tipos de serviços dentro do filtro atual)
    ranking_servicos = (
        servicos_qs.values("nome_servico")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )

    # 6. Lista de tipos de serviços únicos (Para preencher o SELECT do filtro)
    tipos_servicos_disponiveis = Servico.objects.values_list('nome_servico', flat=True).distinct().order_by('nome_servico')

    # 7. Gráfico de Evolução (Últimos 6 meses - Baseado no filtro)
    ultimos_6_meses = (
        servicos_qs.exclude(status="Pendente")
        .annotate(mes=TruncMonth('data_servico'))
        .values('mes')
        .annotate(total=Count('id'))
        .order_by('-mes')[:6]
    )
    
    dados_grafico = {
        "labels": [item['mes'].strftime("%m/%Y") for item in reversed(ultimos_6_meses)],
        "valores": [item['total'] for item in reversed(ultimos_6_meses)]
    }

    # 8. Gráfico Donut (Distribuição por Localidade)
    dict_choices_all = dict(Propriedade._meta.get_field('localidade').choices)
    dados_brutos = servicos_qs.values('propriedade__localidade').annotate(total=Count('id'))
    distribuicao_regiao = [
        {
            'label': dict_choices_all.get(item['propriedade__localidade'], "Não Informado"), 
            'total': item['total']
        } for item in dados_brutos
    ]

    context = {
        "total_mes": total_mes,
        "total_pendentes": total_pendentes,
        "total_servicos_filtrados": total_servicos_filtrados,
        "ranking_servicos": ranking_servicos,
        "tipos_servicos_disponiveis": tipos_servicos_disponiveis,
        "servicos_realizados_lista": servicos_realizados_lista,
        "servicos_pendentes": servicos_pendentes,
        "grafico_dados": json.dumps(dados_grafico),
        "distribuicao_json": json.dumps(distribuicao_regiao),
        "lista_localidades_choices": Propriedade._meta.get_field('localidade').choices,
        "localidade_nome_exibicao": localidade_nome_exibicao,
        "titulo_painel": f"Evolução: {localidade_nome_exibicao}",
        "subtitulo_lista": f"Pendências: {localidade_nome_exibicao}",
    }
    return render(request, template_name, context)

@login_required
def relatorio_excel(request):
    hoje = timezone.localdate()
    localidade = request.GET.get('localidade')
    servico_tipo = request.GET.get('servico_tipo')

    servicos = Servico.objects.all()
    if localidade:
        servicos = servicos.filter(propriedade__localidade=localidade)
    if servico_tipo:
        servicos = servicos.filter(nome_servico=servico_tipo)

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    response["Content-Disposition"] = f'attachment; filename="relatorio_{hoje}.xlsx"'

    wb = Workbook()
    ws = wb.active
    ws.title = "Serviços Filtrados"

    # Cabeçalho
    colunas = ['Data', 'Produtor', 'Serviço', 'Localidade', 'Status']
    ws.append(colunas)
    
    for s in servicos:
        ws.append([
            s.data_servico.strftime("%d/%m/%Y") if s.data_servico else "",
            s.propriedade.pessoa.nome,
            s.nome_servico,
            s.propriedade.get_localidade_display(),
            s.status
        ])

    wb.save(response)
    return response