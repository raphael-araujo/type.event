from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.shortcuts import redirect, render

from .utils import email_is_valid, password_is_valid, username_is_valid


def cadastro(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        senha = request.POST['senha']
        confirmar_senha = request.POST['confirmar_senha']

        if not username_is_valid(request, username):
            return redirect(to='cadastro')

        if not email_is_valid(request, email):
            return redirect(to='cadastro')

        if not password_is_valid(request, senha, confirmar_senha):
            return redirect(to='cadastro')

        user = User.objects.filter(username=username)

        if user.exists():
            messages.add_message(
                request,
                constants.WARNING,
                message='Este nome de usuário já está cadastrado.'
            )
            return redirect(to='cadastro')

        user_email = User.objects.filter(email=email)

        if user_email.exists():
            messages.add_message(
                request,
                constants.WARNING,
                message='Este email já está cadastrado.'
            )
            return redirect(to='cadastro')

        try:
            novo_usuario = User.objects.create_user(username, email, senha)
            novo_usuario.save()

            messages.add_message(
                request,
                constants.SUCCESS,
                message='Usuário cadastrado com sucesso.'
            )
            return redirect(to='login')
        except:
            messages.add_message(
                request,
                constants.ERROR,
                message='Erro interno do sistema.'
            )
            return redirect(to='cadastro')
    else:
        return render(request, 'cadastro.html')
