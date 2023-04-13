from django.contrib import messages


def evento_is_valid(request, nome, descricao, data_inicio, data_termino, carga_horaria,
                 logo, cor_principal, cor_secundaria, cor_fundo):

    if (not logo or len(nome.strip()) == 0 or len(descricao.strip()) == 0
            or len(data_inicio.strip()) == 0 or len(data_termino.strip()) == 0
            or len(carga_horaria.strip()) == 0 or len(cor_principal) == 0
            or len(cor_secundaria.strip()) == 0 or len(cor_fundo.strip()) == 0):

        messages.error(request, message='Preencha todos os campos.')
        return False

    if logo.size > 100_000_000:
        messages.error(
            request, message='A logo do evento deve ter menos de 10MB.')
        return False

    return True
