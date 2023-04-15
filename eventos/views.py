from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify

from .models import Evento
from .utils import evento_is_valid


@login_required(login_url='login')
def novo_evento(request):
    if request.method == 'POST':
        nome = request.POST["nome"]
        descricao = request.POST["descricao"]
        data_inicio = request.POST["data_inicio"]
        data_termino = request.POST["data_termino"]
        carga_horaria = request.POST["carga_horaria"]

        logo = request.FILES.get("logo")

        cor_principal = request.POST["cor_principal"]
        cor_secundaria = request.POST["cor_secundaria"]
        cor_fundo = request.POST["cor_fundo"]

        if not evento_is_valid(request, nome, descricao, data_inicio, data_termino,
                               carga_horaria, logo, cor_principal, cor_secundaria, cor_fundo):
            return redirect(to='novo_evento')

        try:
            evento = Evento.objects.create(
                criador=request.user,
                nome=nome,
                descricao=descricao,
                data_inicio=data_inicio,
                data_termino=data_termino,
                carga_horaria=carga_horaria,
                logo=logo,
                cor_principal=cor_principal,
                cor_secundaria=cor_secundaria,
                cor_fundo=cor_fundo
            )
            evento.save()
            evento.slug = slugify(f'{evento.nome} {evento.id}')
            evento.save()

            messages.success(request, message='Evento cadastrado com sucesso!')
            return redirect(to='gerenciar_eventos')

        except:
            messages.error(request, message='Erro interno do sistema.')
            return request(to='novo_evento')

    return render(request, 'novo_evento.html')


@login_required(login_url='login')
def gerenciar_eventos(request):
    eventos = Evento.objects.filter(criador=request.user)

    filtro_titulo = request.GET.get('titulo')
    if filtro_titulo:
        eventos = eventos.filter(nome__icontains=filtro_titulo)

    return render(request, 'gerenciar_eventos.html', {'eventos': eventos})


@login_required(login_url='login')
def inscricao(request, slug):
    evento = get_object_or_404(Evento, slug=slug)

    if request.method == 'POST':
        if request.user in evento.participantes.all():
            messages.error(request, message='Você já se inscreveu neste evento.')
            return redirect(to='inscricao', slug=slug)

        evento.participantes.add(request.user)
        evento.save()
        messages.success(request, message='Inscrição realizada com sucesso.')
        return redirect(to='inscricao', slug=slug)
    else:
        return render(request, 'inscricao_evento.html', {'evento': evento})


@login_required(login_url='login')
def participantes_evento(request, slug):
    evento = get_object_or_404(Evento, slug=slug)
    participantes = evento.participantes.all()
    
    if evento.criador != request.user:
        raise Http404('Esse evento não é seu.')
    
    context = {
        'evento': evento,
        'participantes': participantes,
        'num_participantes': participantes[:5]
    }

    return render(request, 'participantes_evento.html', context)
