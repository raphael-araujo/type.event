from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse


class CadastroViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='testuser', password='Newpass123', email='test@example.com')

    def test_status_code_200(self):
        response = self.client.get(reverse('cadastro'))
        self.assertEquals(response.status_code, 200)

    def test_template_used(self):
        response = self.client.get(reverse('cadastro'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'cadastro.html')

    def test_cadastro_with_valid_data(self):
        response = self.client.post(reverse('cadastro'), {
            'username': 'newuser123',
            'email': 'newuser@example.com',
            'senha': 'Newpass123',
            'confirmar_senha': 'Newpass123'
        })
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser123').exists())

    def test_cadastro_with_empty_username(self):
        response = self.client.post(reverse('cadastro'), {
            'username': '',
            'email': 'newuser@example.com',
            'senha': 'NewPass123',
            'confirmar_senha': 'NewPass123'
        })
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse('cadastro'))
        self.assertFalse(User.objects.filter(
            email='newuser@example.com').exists())

    def test_cadastro_with_empty_email(self):
        response = self.client.post(reverse('cadastro'), {
            'username': 'newuser',
            'email': '',
            'senha': 'Newpass123',
            'confirmar_senha': 'Newpass123'
        })
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse('cadastro'))
        self.assertFalse(User.objects.filter(email='').exists())

    def test_cadastro_with_mismatched_passwords(self):
        # assuming password_is_valid function checks for matching passwords
        response = self.client.post(reverse('cadastro'), {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'senha': 'Newpass123',
            'confirmar_senha': 'Newpass12'
        })
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse('cadastro'))
        self.assertFalse(User.objects.filter(username='newuser').exists())

    def test_cadastro_with_existing_username(self):
        response = self.client.post(reverse('cadastro'), {
            'username': 'testuser',
            'email': 'newuser@example.com',
            'senha': 'Newpass123',
            'confirmar_senha': 'Newpass123'
        })
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse('cadastro'))

    def test_cadastro_with_existing_email(self):
        response = self.client.post(reverse('cadastro'), {
            'username': 'newuser',
            'email': 'test@example.com',
            'senha': 'Newpass123',
            'confirmar_senha': 'Newpass123'
        })
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse('cadastro'))


class LoginViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='raphael', email='raphael@mail.com', password='password123')

    def test_status_code_200(self):
        response = self.client.get(reverse('login'))
        self.assertEquals(response.status_code, 200)

    def test_template_used(self):
        response = self.client.get(reverse('login'))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

    def test_login_with_valid_credentials(self):
        response = self.client.login(
            username='raphael', password='password123')
        self.assertTrue(response)

        response = self.client.post(reverse('login'), {
            'username': 'raphael',
            'senha': 'password123'
        })
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse('gerenciar_eventos'))

    def test_login_with_invalid_credentials(self):
        response = self.client.login(
            username='raphael', password='password123wrong')
        self.assertFalse(response)

        response = self.client.post(reverse('login'), {
            'username': 'raphael',
            'senha': 'password123wrong'
        })
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))

    def test_login_with_email(self):
        response = self.client.login(
            username='raphael', password='password123')
        self.assertTrue(response)

        response = self.client.post(reverse('login'), {
            'username': 'raphael@mail.com',
            'senha': 'password123'
        })
        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse('gerenciar_eventos'))


class LogoutViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(
            username='raphael', password='password123')

    def test_logout(self):
        self.client.login(username='raphael', password='password123')
        response = self.client.get(reverse('logout'))

        self.assertEquals(response.status_code, 302)
        self.assertRedirects(response, reverse('login'))
        self.assertFalse(response.wsgi_request.user.is_authenticated)
