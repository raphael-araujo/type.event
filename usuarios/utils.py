import re

from django.contrib import messages
from django.contrib.messages import constants


def username_is_valid(request, usuario):
    """verifica se o campo de nome de usuário está vazio"""
    if len(usuario.strip()) == 0:
        messages.add_message(request, constants.ERROR,
                             'O campo "Username" está vazio')
        return False

    return True


def email_is_valid(request, email):
    """verifica se o campo e-mail está vazio"""
    if len(email.strip()) == 0:
        messages.add_message(request, constants.ERROR,
                             'O campo "E-mail" está vazio')
        return False

    return True


def password_is_valid(request, senha, confirmar_senha):
    """verifica se a senha é válida."""

    if len(senha.strip()) == 0 or len(confirmar_senha.strip()) == 0:
        messages.add_message(request, constants.ERROR,
                             'Os campos "Senha" e "Confirmar senha" são obrigatórios')

    if len(senha) < 6:
        messages.add_message(request, constants.ERROR,
                             'Sua senha deve conter 6 ou mais caracteres')
        return False

    if not senha == confirmar_senha:
        messages.add_message(request, constants.ERROR,
                             'As senhas não coincidem!')
        return False

    if not re.search('[A-Z]', senha):
        messages.add_message(request, constants.ERROR,
                             'Sua senha deve conter ao menos uma letra maiúscula')
        return False

    if not re.search('[a-z]', senha):
        messages.add_message(request, constants.ERROR,
                             'Sua senha deve conter ao menos uma letra minúscula')
        return False

    if not re.search('[0-9]', senha):
        messages.add_message(request, constants.ERROR,
                             'Sua senha deve conter pelo menos um número')
        return False

    return True
