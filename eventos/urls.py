from django.urls import path

from . import views


urlpatterns = [
    path('novo_evento/', views.novo_evento, name='novo_evento'),
    path('gerenciar_eventos/', views.gerenciar_eventos, name='gerenciar_eventos'),
    path('inscricao/<slug:slug>/', views.inscricao, name='inscricao'),
    path('participantes_evento/<slug:slug>/', views.participantes_evento, name='participantes_evento'),
    path('exportar_csv/<slug:slug>/', views.exportar_csv, name='exportar_csv'),
    path('certificados_evento/<slug:slug>/', views.certificados_evento, name='certificados_evento'),
    path('gerar_certificado/<slug:slug>/', views.gerar_certificado, name='gerar_certificado'),
]
