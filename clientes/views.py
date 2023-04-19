from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from eventos.models import Certificado, Evento


@login_required(login_url='login')
def meus_eventos(request):
    eventos = Evento.objects.filter(participantes__username=request.user)
    certificados = Certificado.objects.filter(participante=request.user)
    print(certificados)
    filtro_titulo= request.GET.get('titulo')

    if filtro_titulo:
        eventos = eventos.filter(nome__icontains=filtro_titulo)

    context = {
        'eventos': eventos,
        'certificados': certificados
    }
    return render(request, 'meus_eventos.html', context)


@login_required(login_url='login')
def meus_certificados(request):
    certificados = Certificado.objects.filter(participante=request.user)
    return render(request, 'meus_certificados.html', {'certificados': certificados})
