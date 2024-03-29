from django.contrib.auth.models import User
from django.db import models


class Evento(models.Model):
    criador = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    nome = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    descricao = models.TextField()
    data_inicio = models.DateField()
    data_termino = models.DateField()
    carga_horaria = models.PositiveIntegerField()
    logo = models.FileField(upload_to='logos')
    participantes = models.ManyToManyField(
        User,
        related_name='evento_participante',
        blank=True
    )

    # paleta de cores:
    cor_principal = models.CharField(max_length=7)
    cor_secundaria = models.CharField(max_length=7)
    cor_fundo = models.CharField(max_length=7)

    def __str__(self):
        return self.nome


class Certificado(models.Model):
    template = models.ImageField(upload_to='certificados')
    participante = models.ForeignKey(User, on_delete=models.DO_NOTHING)
    evento = models.ForeignKey(Evento, on_delete=models.DO_NOTHING)

    def __str__(self) -> str:
        return f'{self.participante.username} - {self.participante.email}'
