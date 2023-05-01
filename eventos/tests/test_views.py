from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from eventos.models import Certificado, Evento


class NovoEventoViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser', email='testuser@example.com', password='Password12345'
        )
        self.client.login(username='testuser', password='Password12345')
        self.url = reverse('novo_evento')

    def test_novo_evento_view_status_code_is_200(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'novo_evento.html')

    def test_novo_evento_view_with_complete_data(self):
        logo = SimpleUploadedFile("file.png", b"file_content", content_type="image/png")
        response = self.client.post(self.url, {
            'nome': 'Teste',
            'descricao': 'Teste de evento',
            'data_inicio': '2023-05-01',
            'data_termino': '2023-05-02',
            'carga_horaria': 8,
            'logo': logo,
            'cor_principal': '#000000',
            'cor_secundaria': '#FFFFFF',
            'cor_fundo': '#CCCCCC'
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('gerenciar_eventos'))

        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Evento cadastrado com sucesso!')

    def test_novo_evento_view_with_incomplete_data(self):
        response = self.client.post(self.url, {
            'nome': '',
            'descricao': 'Teste de evento',
            'data_inicio': '2023-05-01',
            'data_termino': '2023-05-02',
            'carga_horaria': 8,
            'logo': '',
            'cor_principal': '#000000',
            'cor_secundaria': '#FFFFFF',
            'cor_fundo': '#CCCCCC'
        })

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url)
        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Preencha todos os campos.')

    def test_if_user_is_redirected_to_login_page_if_they_are_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/usuarios/login/?next=/eventos/novo_evento/')


class GerenciarEventosViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='Password12345')
        self.client.login(username='testuser', password='Password12345')
        for i in range(1, 4):
            Evento.objects.create(
                criador=self.user,
                nome=f'Test Event{i}',
                slug=f'test-event{i}',
                descricao=f'This is a test event{i}',
                data_inicio='2023-01-01',
                data_termino='2023-01-02',
                carga_horaria=8,
                cor_principal='#ffffff',
                cor_secundaria='#000000',
                cor_fundo='#cccccc'
            )
        self.url = reverse('gerenciar_eventos')

    def test_gerenciar_eventos_view(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gerenciar_eventos.html')
        self.assertEqual(Evento.objects.filter(criador=self.user).count(), 3)
        self.assertQuerysetEqual(response.context['eventos'], Evento.objects.all(), ordered=False)

    def test_gerenciar_eventos_view_with_filter(self):
        filtro = 'Event1'
        response = self.client.get(self.url, {'titulo': filtro})

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gerenciar_eventos.html')
        self.assertQuerysetEqual(
            response.context['eventos'], Evento.objects.filter(nome__icontains=filtro), ordered=False
        )

    def test_if_user_is_redirected_to_login_page_if_they_are_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/usuarios/login/?next=/eventos/gerenciar_eventos/')


class InscricaoViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='Password12345')
        self.client.login(username='testuser', password='Password12345')
        logo = SimpleUploadedFile("file.png", b"file_content", content_type="image/png")
        self.evento = Evento.objects.create(
            criador=self.user,
            nome=f'Test Event',
            slug=f'test-event',
            descricao=f'This is a test event',
            data_inicio='2023-01-01',
            data_termino='2023-01-02',
            carga_horaria=8,
            logo=logo,
            cor_principal='#ffffff',
            cor_secundaria='#000000',
            cor_fundo='#cccccc'
        )
        self.url = reverse('inscricao', args=[self.evento.slug])

    def test_view_inscricao_status_code_is_200(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'inscricao_evento.html')

    def test_if_the_user_can_subscribe_in_the_event(self):
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, self.url)
        self.assertIn(self.user, self.evento.participantes.all())

    def test_error_if_user_already_registered(self):
        self.evento.participantes.add(self.user)
        response = self.client.post(self.url)
        messages = list(response.wsgi_request._messages)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Você já se inscreveu neste evento.')

    def test_if_user_is_redirected_to_login_page_if_they_are_not_logged_in(self):
        self.client.logout()
        response = self.client.post(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/usuarios/login/?next=/eventos/inscricao/test-event/')


class ParticipantesEventoViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='Password12345')
        self.client.login(username='testuser', password='Password12345')
        logo = SimpleUploadedFile("file.png", b"file_content", content_type="image/png")
        self.evento = Evento.objects.create(
            criador=self.user,
            nome=f'Test Event',
            slug=f'test-slug',
            descricao=f'This is a test event',
            data_inicio='2023-01-01',
            data_termino='2023-01-02',
            carga_horaria=8,
            logo=logo,
            cor_principal='#ffffff',
            cor_secundaria='#000000',
            cor_fundo='#cccccc'
        )
        self.url = reverse('participantes_evento', args=[self.evento.slug])

    def test_view_participantes_status_code_is_200(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'participantes_evento.html')

    def test_context_contains_correct_data(self):
        response = self.client.get(self.url)
        self.assertEqual(response.context['evento'], self.evento)

    def test_status_code_404_if_user_is_not_event_creator(self):
        self.other_user = User.objects.create_user(username='otheruser', password='Otherpass123')
        self.client.login(username='otheruser', password='Otherpass123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)

    def test_if_user_is_redirected_to_login_page_if_they_are_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/usuarios/login/?next=/eventos/participantes_evento/test-slug/')


class ExportarCSVViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='Password12345')
        self.client.login(username='testuser', password='Password12345')
        logo = SimpleUploadedFile("file.png", b"file_content", content_type="image/png")
        self.evento = Evento.objects.create(
            criador=self.user,
            nome=f'Test Event',
            slug=f'test-slug',
            descricao=f'This is a test event',
            data_inicio='2023-01-01',
            data_termino='2023-01-02',
            carga_horaria=8,
            logo=logo,
            cor_principal='#ffffff',
            cor_secundaria='#000000',
            cor_fundo='#cccccc'
        )
        self.url = reverse('exportar_csv', args=[self.evento.slug])

    def test_if_view_generates_csv(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

        token = response.url.split('/')[-1]
        file = SimpleUploadedFile(name=token, content=b"username, email", content_type="text/csv")
        self.assertEqual(file.name, token)

    def test_status_code_404_if_user_is_not_event_creator(self):
        self.other_user = User.objects.create_user(username='otheruser', password='Otherpass123')
        self.client.login(username='otheruser', password='Otherpass123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)

    def test_if_user_is_redirected_to_login_page_if_they_are_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, '/usuarios/login/?next=/eventos/exportar_csv/test-slug/')


class CertificadosEventoViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='Password12345')
        self.client.login(username='testuser', password='Password12345')
        logo = SimpleUploadedFile("file.png", b"file_content", content_type="image/png")
        self.evento = Evento.objects.create(
            criador=self.user,
            nome=f'Test Event',
            slug=f'test-event',
            descricao=f'This is a test event',
            data_inicio='2023-01-01',
            data_termino='2023-01-02',
            carga_horaria=8,
            logo=logo,
            cor_principal='#ffffff',
            cor_secundaria='#000000',
            cor_fundo='#cccccc'
        )
        self.url = reverse('certificados_evento', args=[self.evento.slug])

    def test_view_certificados_evento_status_code_is_200(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['evento'], self.evento)
        self.assertTemplateUsed(response, 'certificados_evento.html')

    def test_status_code_404_if_user_is_not_event_creator(self):
        self.other_user = User.objects.create_user(username='otheruser', password='Otherpass123')
        self.client.login(username='otheruser', password='Otherpass123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)

    def test_if_user_is_redirected_to_login_page_if_they_are_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/usuarios/login/?next=/eventos/certificados_evento/{self.evento.slug}/')


class GerarCertificadoViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='Password12345')
        self.other_user = User.objects.create_user(username='otheruser', password='Otherpass123')
        self.client.login(username='testuser', password='Password12345')

        logo = SimpleUploadedFile("file.png", b"file_content", content_type="image/png")
        self.evento = Evento.objects.create(
            criador=self.user,
            nome=f'Test Event',
            slug=f'test-event',
            descricao=f'This is a test event',
            data_inicio='2023-01-01',
            data_termino='2023-01-02',
            carga_horaria=8,
            logo=logo,
            cor_principal='#ffffff',
            cor_secundaria='#000000',
            cor_fundo='#cccccc'
        )
        self.evento.participantes.add(self.user, self.other_user)
        self.url = reverse('gerar_certificado', args=[self.evento.slug])

    def test_status_code_404_if_user_is_not_event_creator(self):
        self.client.login(username='otheruser', password='Otherpass123')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)

    def test_certificates_are_generated_successfully(self):
        response = self.client.get(self.url)
        self.assertRedirects(response, reverse('certificados_evento', args=[self.evento.slug]))
        self.assertEqual(response.status_code, 302)

        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Certificados gerados com sucesso')

        # Verifique se os certificados foram criados para todos os participantes do evento
        for participante in self.evento.participantes.all():
            self.assertTrue(Certificado.objects.filter(participante=participante, evento=self.evento).exists())


class ProcurarCertificadoViewTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='Password12345')
        self.client.login(username='testuser', password='Password12345')
        logo = SimpleUploadedFile("file.png", b"file_content", content_type="image/png")
        self.evento = Evento.objects.create(
            criador=self.user,
            nome=f'Test Event',
            slug=f'test-event',
            descricao=f'This is a test event',
            data_inicio='2023-01-01',
            data_termino='2023-01-02',
            carga_horaria=8,
            logo=logo,
            cor_principal='#ffffff',
            cor_secundaria='#000000',
            cor_fundo='#cccccc'
        )
        self.url = reverse('procurar_certificado', args=[self.evento.slug])

    def test_event_does_not_exist(self):
        response = self.client.get(reverse('procurar_certificado', args=['nonexistent-slug']))
        self.assertEqual(response.status_code, 404)

    def test_event_does_not_belong_to_user(self):
        self.other_user = User.objects.create_user(username='otheruser', password='otherpass')
        self.client.login(username='otheruser', password='otherpass')
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 404)

    def test_certificado_not_found(self):
        response = self.client.post(self.url, data={'email': 'nonexistent@example.com'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('certificados_evento', args=[self.evento.slug]))

        messages = list(response.wsgi_request._messages)
        self.assertEqual(len(messages), 1)
        self.assertEqual(str(messages[0]), 'Certificado não encontrado.')

    def test_certificado_was_found(self):
        participante = User.objects.create_user(username='participante', email='participante@example.com')
        template = SimpleUploadedFile(f"teste.png", b"template_content", content_type="image/png")
        certificado = Certificado.objects.create(
            template=template,
            evento=self.evento,
            participante=participante
        )
        response = self.client.post(self.url, data={'email': 'participante@example.com'})

        self.assertEqual(response.url, certificado.template.url)
