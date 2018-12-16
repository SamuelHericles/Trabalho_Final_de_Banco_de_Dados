#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Módulo define funções responsáveis para checar sanidade de valores.

Cada função de check de sanidade deve receber uma string e retornar
uma instância das classes filhas de ErrorMessage: sendo Ok ou Error.
"""


from datetime import datetime
from teca import database


class ErrorMessage(object):
    """Classe Pai de Error ou OK"""
    def __init__(self, message, status):
        self.message = message
        self.status = status

    def __bool__(self):
        return self.status

    def __str__(self):
        return self.message


class Error(ErrorMessage):
    """Classe Error que relaciona um booleano False a uma mensagem."""
    def __init__(self, message):
        super().__init__(message, False)


class Ok(ErrorMessage):
    """Classe Ok que relaciona um booleano True a uma mensagem."""
    def __init__(self, message):
        super().__init__(message, True)


def data(data_string, format='%Y-%m-%d'):
    """Método para checar a formatação e os dados da data inserida."""
    try:
        datetime.strptime(data_string, format)
        return Ok("Data é válida")
    except Exception:
        return Error("Data é inválida")


def matricula(matricula):
    """Método para checar se a matricula é um inteiro positivo."""
    if not matricula.isdecimal():
        return Error("Matricula deve ser um inteiro positivo!")
    elif database.Usuario.select(matricula) is not None:
        return Error("Matrícula ocupada!")
    else:
        return Ok("Matrícula ok!")


def nao_vazia(entrada):
    """Método pra checar se uma entrada é vazia."""
    if len(entrada) == 0:
        return Error("Entrada não pode ser vazia!")
    return Ok("Entrada ok!")


def nome(nome):
    """Método para checar se o nome do usuário contém apenas letras ou espaçamentos."""
    if not nome.replace(' ', '').isalpha():
        return Error("Nome deve ter apenas letras!")
    elif len(nome) == 0:
        return Error("Nome não pode ser vazio!")
    else:
        return Ok("Nome ok!")


def endereco(endereco):
    """Método para checar se o endereço não é um campo vazio."""
    if len(endereco) == 0:
        return Error("Endereço não pode ser vazio!")
    else:
        return Ok("Endereço ok!")


def senha(senha):
    """Método para checar se no campo senha foi inserido algo."""
    if len(senha) == 0:
        return Error("Senha não pode ser vazia!")
    else:
        return Ok("Senha ok!")


def cpf(cpf):
    """Metódo para checar se o cpf contém exatamente 11 digitos."""
    if len(cpf) != 11 and not cpf.isdecimal():
        return Error("cpf deve possuir 11 dígitos!")
    else:
        return Ok("cpf ok!")


def isbn(isbn):
    """Método para checar se o isbn contém exatamente 13 digitos."""
    if len(isbn) != 13 and not isbn.isdecimal():
        return Error("isbn deve possuir 13 dígitos!")
    else:
        return Ok("isbn ok!")


def nickname(nickname):
    """Método para checar se o nickaname não está vazio ou já existe."""
    if len(database.Usuario.filter(nickname=nickname)) != 0:
        return Error("Nickname já existe!")
    elif len(nickname) == 0:
        return Error("Nickname não pode ser vazio!")
    else:
        return Ok("Nickname ok!")


def telefone(telefone):
    """Métodos para checar se os telefones contém apenas números entre 8 e 12 digitos."""
    if not telefone.isdecimal():
        return Error("Telefone deve conter apenas dígitos!")
    elif len(telefone) not in range(8, 12):
        return Error("Telefone deve conter entre 8 a 12 dígitos!")
    else:
        return Ok("Telefone ok!")


def emprestimo(usuario, livro):
    """Método para checar as tramitações de empréstimos do usuário."""
    emprestimos = usuario.emprestimos
    extra = usuario.extra
    if livro.disponiveis <= 0:
        return Error("Livro indisponível para empréstimo!")
    elif extra is None:
        return Error(f"Usuário possuí dados corrompidos na tabela {usuario.tipo!r}! Contacte o administrador.")  # noqa
    elif len(emprestimos) >= extra.livros_max:
        return Error(f"Usuário já alcançou o limite de {extra.livros_max} empréstimos!")  # noqa
    elif any(livro.isbn == e.isbn for e in emprestimos):
        return Error("Usuário já possuí um exemplar desse livro emprestado.")
    elif any(e.vencido for e in emprestimos):
        return Error("Usuário possui empréstimo(s) vencido(s)!")
    elif (livro.disponiveis - len(livro.reservas)) <= 0:
        res = database.Reserva.filter(matricula=usuario.matricula,
                                      isbn=livro.isbn)
        if len(res) != 0 and res[0].data_contemplado is not None:
            return Ok("Emprestimo ok, usuario possui reserva contemplada.")
        else:
            return Error("Livro disponivel apenas para reservas contempladas!")
    return Ok("Empréstimo ok!")


def entrada(prompt, funcao_check):
    """Método para continuar lendo uma entrada até receber um valor válido.

    Parâmetros
    ----------
    prompt: uma string que será apresentada para o usuário
    funcao_check: uma função que recebe uma string e retorna Ok/Error como resultado
    """
    while True:
        entrada = input(prompt)
        status = funcao_check(entrada)
        if status:
            break
        else:
            print(status)
    return entrada


def ask(ask):
    """Método para checar se digitou y/Y ou n/N."""
    if ask.lower() not in ('y', 'n'):
        return Error("Entrada inválida")
    else:
        return Ok("Entrada ok!")
