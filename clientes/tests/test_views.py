from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from eventos.models import Certificado, Evento


class MeusEventosViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', email='test@mail.com', password='Password12345')
        cls.criador = User.objects.create_user(username='testcriador', password='Password123456')
        logo = SimpleUploadedFile("file.png", b"file_content", content_type="image/png")
        cls.evento1 = Evento.objects.create(
            criador=cls.criador,
            nome=f'Test Event1',
            slug=f'test-event1',
            descricao=f'This is a test event1',
            data_inicio='2023-01-01',
            data_termino='2023-01-02',
            carga_horaria=8,
            logo=logo,
            cor_principal='#ffffff',
            cor_secundaria='#000000',
            cor_fundo='#cccccc'
        )
        cls.evento1.participantes.add(cls.user)

        template = SimpleUploadedFile(f"teste.png", b"template_content", content_type="image/png")
        Certificado.objects.create(
            template=template,
            participante=cls.user,
            evento=cls.evento1
        )
        cls.url = reverse('meus_eventos')

    def test_meus_eventos_view(self):
        self.client.login(username='testuser', password='Password12345')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meus_eventos.html')
        self.assertQuerysetEqual(response.context['eventos'], Evento.objects.filter(
            participantes__username=self.user))
        self.assertQuerysetEqual(response.context['certificados'], Certificado.objects.filter(
            participante=self.user))

    def test_meus_eventos_view_with_filter(self):
        self.client.login(username='testuser', password='Password12345')
        response = self.client.get(self.url, {'titulo': 'Evento 2'})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meus_eventos.html')
        self.assertQuerysetEqual(response.context['eventos'], [])

    def test_if_user_is_redirected_to_login_page_if_they_are_not_logged_in(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/usuarios/login/?next=/clientes/meus_eventos/')


class MeusCertificadosViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='testuser', email='test@mail.com', password='Password12345')
        cls.criador = User.objects.create_user(username='testcriador', password='Password123456')
        logo = SimpleUploadedFile("file.png", b"file_content", content_type="image/png")
        cls.evento = Evento.objects.create(
            criador=cls.criador,
            nome=f'Test Event1',
            slug=f'test-event1',
            descricao=f'This is a test event1',
            data_inicio='2023-01-01',
            data_termino='2023-01-02',
            carga_horaria=8,
            logo=logo,
            cor_principal='#ffffff',
            cor_secundaria='#000000',
            cor_fundo='#cccccc'
        )
        cls.evento.participantes.add(cls.user)

        template = SimpleUploadedFile(f"teste.png", b"template_content", content_type="image/png")
        cls.certificado = Certificado.objects.create(
            template=template,
            participante=cls.user,
            evento=cls.evento
        )
        cls.url = reverse('meus_certificados')

    def test_meus_certificados_view(self):
        self.client.login(username='testuser', password='Password12345')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'meus_certificados.html')

    def test_meus_certificados_view_with_certificates(self):
        self.client.login(username='testuser', password='Password12345')
        response = self.client.get(self.url)
        self.assertQuerysetEqual(response.context['certificados'], Certificado.objects.filter(participante=self.user))

    def test_if_user_is_redirected_to_login_page_if_they_are_not_logged_in(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/usuarios/login/?next=/clientes/meus_certificados/')
