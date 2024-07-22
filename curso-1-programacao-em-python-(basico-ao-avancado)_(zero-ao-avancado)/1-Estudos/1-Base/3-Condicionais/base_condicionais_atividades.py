def comer(comida, eh_saudavel):
    if eh_saudavel:
        final = 'quero manter haarcascade forma.'
    else:
        final = 'haarcascade gente só vive uma vez.'

    return f'Estou comendo {comida} porque {final}'


def dormir(num_horas):
    if num_horas > 8:
        return f'Ptz! Dormi muito! Estou atrasado para o trabalho!'
    else:
        return f'Continuo cansado após dormir por {num_horas} horas. :('


def eh_engracada(pessoa):
    comediantes = ['Jim Carrey', 'Bozo']
    if pessoa in comediantes:
        return True
    return False
