from django.contrib.auth.models import User
from django.test import TestCase
from eventos.models import Certificado, Evento


class EventoModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        # Set up non-modified objects used by all test methods
        user = User.objects.create(username='testuser')
        Evento.objects.create(
            criador=user,
            nome='Test Event',
            slug='test-event',
            descricao='This is a test event',
            data_inicio='2023-01-01',
            data_termino='2023-01-02',
            carga_horaria=8,
            cor_principal='#ffffff',
            cor_secundaria='#000000',
            cor_fundo='#cccccc'
        )

    def test_criador_label(self):
        evento = Evento.objects.get(id=1)
        field_label = evento._meta.get_field('criador').verbose_name
        self.assertEqual(field_label, 'criador')

    def test_nome_label(self):
        evento = Evento.objects.get(id=1)
        field_label = evento._meta.get_field('nome').verbose_name
        self.assertEqual(field_label, 'nome')

    def test_slug_label(self):
        evento = Evento.objects.get(id=1)
        field_label = evento._meta.get_field('slug').verbose_name
        self.assertEqual(field_label, 'slug')

    def test_descricao_label(self):
        evento = Evento.objects.get(id=1)
        field_label = evento._meta.get_field('descricao').verbose_name
        self.assertEqual(field_label, 'descricao')

    def test_data_inicio_label(self):
        evento = Evento.objects.get(id=1)
        field_label = evento._meta.get_field('data_inicio').verbose_name
        self.assertEqual(field_label, 'data inicio')

    def test_data_termino_label(self):
        evento = Evento.objects.get(id=1)
        field_label = evento._meta.get_field('data_termino').verbose_name
        self.assertEqual(field_label, 'data termino')

    def test_carga_horaria_label(self):
        evento = Evento.objects.get(id=1)
        field_label = evento._meta.get_field('carga_horaria').verbose_name
        self.assertEqual(field_label, 'carga horaria')

    def test_object_name_is_nome(self):
        evento = Evento.objects.get(id=1)
        expected_object_name = f'{evento.nome}'
        self.assertEqual(expected_object_name, str(evento))

    def test_data_inicio_less_data_termino(self):
        evento = Evento.objects.get(id=1)
        self.assertLess(evento.data_inicio, evento.data_termino)

    def test_participantes(self):
        user1 = User.objects.create(username='testuser1')
        user2 = User.objects.create(username='testuser2')
        evento = Evento.objects.get(id=1)
        evento.participantes.add(user1, user2)
        self.assertEqual(evento.participantes.count(), 2)


class CertificadoTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create(
            username='testuser', email='testuser@example.com')
        self.evento = Evento.objects.create(
            criador=self.user,
            nome='Teste Evento',
            slug='teste-evento',
            descricao='This is a teste evento',
            data_inicio='2023-01-03',
            data_termino='2023-01-04',
            carga_horaria=8,
            cor_principal='#ffffff',
            cor_secundaria='#000000',
            cor_fundo='#cccccc'
        )
        self.certificado = Certificado.objects.create(
            template='certificados/teste.jpg',
            participante=self.user,
            evento=self.evento
        )

    def test_create_certificado(self):
        certificado = Certificado.objects.create(
            template='certificados/teste2.jpg',
            participante=self.user,
            evento=self.evento
        )
        self.assertEqual(Certificado.objects.count(), 2)
        self.assertEqual(certificado.template, 'certificados/teste2.jpg')
        self.assertEqual(certificado.participante, self.user)
        self.assertEqual(certificado.evento, self.evento)

    def test_participante_validation(self):
        with self.assertRaises(Exception):
            Certificado.objects.create(
                template='certificados/teste3.jpg',
                evento=self.evento
            )

    def test_object_name_is_username_and_email(self):
        self.assertEqual(str(self.certificado), 'testuser - testuser@example.com')
