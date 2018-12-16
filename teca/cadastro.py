#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Módulo responsável pelo cadastro do usuário pelo terminal.

Utiliza a interface de comunicação com o banco de dados database.py
para realizar as inserções.
Faz-se uso das funções de verificação de sanidade do módulo
check.py, como matricula, telefone, nome, endereço, senha.
"""


from teca import check
from teca import database
from teca.term import menu_enumeracao
import getpass
from mysql.connector.errors import DatabaseError


def entrada_usuario_comum():
    """Realiza a leitura dos campos da tabela usuário."""
    matricula = check.entrada('> Digite sua matricula: ', check.matricula)
    nome = check.entrada('> Digite seu nome completo: ', check.nome)
    endereco = check.entrada('> Digite seu endereço: ', check.endereco)
    tipos = {
        '1': 'aluno',
        '2': 'professor',
        '3': 'funcionario'
    }
    print('> Você é aluno, professor ou outro funcionário?')
    escolha = menu_enumeracao(tipos)
    tipo = tipos[escolha]
    nickname = check.entrada('> Digite um nickname para acesso a sua conta: ',
                             check.nickname)

    while True:
        senha_cadastro = getpass.getpass(prompt='> Digite uma senha: ')
        status = check.senha(senha_cadastro)
        if status:
            break
        else:
            print(status)

    permissao = 'usuario'
    senha_hash = database.senha_hash(senha_cadastro)
    usuario = database.Usuario(matricula, nickname,
                               senha_hash, nome,
                               endereco, tipo, permissao)
    return usuario


def entrada_curso():
    """Dado os cursos disponíveis, realiza leitura de um código de curso."""
    cursos = {str(c.cod_curso): c.nome_curso
              for c in database.Curso.select_all()}
    print('> Digite o código de seu curso')
    cod_curso = menu_enumeracao(cursos)
    return cod_curso


def entrada_aluno(matricula):
    """Realiza a leitura dos campos da tabela aluno."""
    cod_curso = entrada_curso()
    print('> Em que ano, mês e dia você entrou na UFC? (YYYY-MM-DD)')
    data_de_ingresso = check.entrada('>>> ', check.data)
    print('> Em que data você vai concluir seu curso? (YYYY-MM-DD)')
    data_de_conclusao = check.entrada('>>> ', check.data)

    aluno = database.Aluno(matricula, data_de_conclusao,
                           data_de_ingresso, cod_curso)
    return aluno


def entrada_professor(matricula):
    """Realiza a leitura dos campos da tabela professor."""
    cod_curso = entrada_curso()

    print('> Em que data você foi contratado pela UFC? (YYYY-MM-DD)')
    data_de_contratacao = check.entrada('>>> ', check.data)
    tipos_regime = {
        '1': 'DE',
        '2': '20H',
        '3': '40H'
    }
    print('> O seu regime de trabalho é de quantas horas?')
    op = menu_enumeracao(tipos_regime)
    regime_de_trabalho = tipos_regime[op]

    prof = database.Professor(matricula, data_de_contratacao,
                              regime_de_trabalho, cod_curso)
    return prof


def entrada_telefones(matricula):
    """Realiza a leitura de N telefones."""
    telefones = []

    while True:
        telefone = check.entrada('> Digite um numero de telefone: ',
                                 check.telefone)
        if telefone in telefones:
            print("Telefone já foi digitado. Ignorado.")
        else:
            telefones.append(telefone)

        ask = check.entrada('> Tem mais algum telefone? (Y/N) ', check.ask)
        if ask.lower() != 'y':
            break

    return [database.Telefones(matricula, t) for t in telefones]


def tela_cadastro_usuario():
    """Tela principal de cadastro do usuário."""
    print('== CADASTRO DE USUÁRIO ==')

    usuario = entrada_usuario_comum()
    telefones = entrada_telefones(usuario.matricula)
    if usuario.tipo == 'aluno':
        extra = entrada_aluno(usuario.matricula)
    elif usuario.tipo == 'professor':
        extra = entrada_professor(usuario.matricula)
    else:
        extra = database.Funcionario(usuario.matricula)

    print("== DADOS INSERIDOS: ")
    for attr, value in usuario.items():
        if attr == 'senha_hash':
            value = '*' * 8
            attr = 'senha'
        print(f"{attr}: {value}")

    for attr, value in extra.items():
        if attr not in extra._primary_key:
            print(f"{attr}: {value}")

    for i, telefone in enumerate(telefones):
        print(f'telefone_{i+1}: {telefone.numero}')
    ask = check.entrada('\nEstá certo os dados que você inseriu? (Y/N): ',
                        check.ask)
    if ask.lower() == 'y':
        usuario.insert()
        for telefone in telefones:
            telefone.insert()

        while True:
            try:
                extra.insert()
                print('USUÁRIO CADASTRADO COM SUCESSO!')
                break
            except DatabaseError:
                print("Data de conclusão prevista menor que a data atual.")
                ask = input("Tentar novamente? (Y/N)")
                if ask.lower() == 'y':
                    print('> Em que data você vai concluir seu curso? (YYYY-MM-DD)')
                    data_de_conclusao = check.entrada('>>> ', check.data)
                    extra.data_de_conclusao_prevista = data_de_conclusao
                else:
                    print('CADASTRO INVÁLIDO! IGNORADO.')
                    usuario.delete()
                    break

    else:
        print('CADASTRO CANCELADO!')
