import csv
import os
import sys
from io import BytesIO
from secrets import token_urlsafe

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.text import slugify
from PIL import Image, ImageDraw, ImageFont

from .models import Certificado, Evento
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


@login_required(login_url='login')
def exportar_csv(request, slug):
    evento = get_object_or_404(Evento, slug=slug)

    if evento.criador != request.user:
        raise Http404('Esse evento não é seu.')

    participantes = evento.participantes.all()

    token = f'{token_urlsafe(6)}.csv'
    path = os.path.join(settings.MEDIA_ROOT, token)

    with open(path, 'w') as arq:
        writer = csv.writer(arq, delimiter=",")
        for participante in participantes:
            x = (participante.username, participante.email)
            writer.writerow(x)

    return redirect(f'/media/{token}')


@login_required(login_url='login')
def certificados_evento(request, slug):
    evento = get_object_or_404(Evento, slug=slug)

    if evento.criador != request.user:
        raise Http404('Esse evento não é seu.')

    quantidade_certificados = evento.participantes.all().count(
    ) - Certificado.objects.filter(evento=evento).count()

    context = {
        'evento': evento,
        'quantidade_certificados': quantidade_certificados
    }

    return render(request, 'certificados_evento.html', context)


@login_required(login_url='login')
def gerar_certificado(request, slug):
    evento = get_object_or_404(Evento, slug=slug)

    if evento.criador != request.user:
        raise Http404('Esse evento não é seu.')

    path_template = os.path.join(
        settings.BASE_DIR, 'templates/static/eventos/img/template_certificado.png')
    path_fonte = os.path.join(
        settings.BASE_DIR, 'templates/static/eventos/fonts/arimo.ttf')
    for participante in evento.participantes.all():
        img = Image.open(path_template)
        draw = ImageDraw.Draw(img)
        fonte_nome = ImageFont.truetype(path_fonte, 60)
        fonte_info = ImageFont.truetype(path_fonte, 30)
        draw.text((230, 651), f"{participante.username}",
                  font=fonte_nome, fill=(0, 0, 0))
        draw.text((761, 782), f"{evento.nome}",
                  font=fonte_info, fill=(0, 0, 0))
        draw.text((816, 849), f"{evento.carga_horaria} horas",
                  font=fonte_info, fill=(0, 0, 0))
        output = BytesIO()
        img.save(output, format="PNG", quality=100)
        output.seek(0)
        img_final = InMemoryUploadedFile(
            output,
            'ImageField',
            f'{token_urlsafe(8)}.png',
            'image/jpeg',
            sys.getsizeof(output),
            None
        )
        try:
            if not Certificado.objects.filter(participante=participante).exists():
                certificado_gerado = Certificado(
                    template=img_final,
                    participante=participante,
                    evento=evento,
                )
                certificado_gerado.save()
        except:
            messages.error(request, message='Erro ao gerar certificados.')
            return redirect(to='certificados_evento', slug=slug)

    messages.success(request, message='Certificados gerados com sucesso')
    return redirect(to='certificados_evento', slug=slug)


def procurar_certificado(request, slug):
    evento = get_object_or_404(Evento, slug=slug)

    if evento.criador != request.user:
        raise Http404('Esse evento não é seu.')

    email = request.POST.get('email')
    certificado = Certificado.objects.filter(
        evento=evento).filter(participante__email=email).first()

    if not certificado:
        messages.warning(request, message='Certificado não encontrado.')
        return redirect(to='certificados_evento', slug=slug)

    return redirect(certificado.template.url)