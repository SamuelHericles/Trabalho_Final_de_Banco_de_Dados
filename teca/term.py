# coding: utf-8


"""Módulo para operações comuns de entrada/saída no terminal.

Utiliza a biblioteca de formatação de tabelas, a tabulate além da
interface de comunicação de banco de dados, a database.py.
"""

from tabulate import tabulate
from teca import database


def sumario_emprestimo(e):
    """Exibi um empréstimo feito no sistema."""
    return f'{e.isbn} / {e.livro.titulo} / {e.data_de_emprestimo}'


def sumario_reserva(r):
    """Exibe uma reserva feita no sistema."""
    return f'{r.isbn} / {r.livro.titulo} / {r.data_de_reserva}'


def sumario_livro(l):
    """Exibe os atributos de um livro da biblioteca."""
    return f'{l.isbn} / {l.titulo} / {l.editora} / {l.ano} / {l.categoria} / {l.disponiveis}'


def sumario_usuario(u):
    """Exibe apenas o usuário e sua matricula."""
    return f'{u.matricula} / {u.nome}'


def imprimir_tabela(tabela):
    """Imprime todas as tuplas da tabela"""
    tuples = tabela.select_all()
    if tabela == database.Usuario:
        for u in tuples:
            u.senha_hash = '***SECRET***'

    rows = [list(row) for row in tuples]
    print(tabulate(rows, tabela._columns, 'psql'))


def menu_enumeracao(opcoes):
    """Constroi um menu de enumeração como pergunta.

    Parâmetros
    ---------
    opcoes: deve ser um dicionário onde a chave é uma string como a
    resposta esperada

    Ex.: opcoes = {'1': 'Opcao A', '2': 'Opcao B'}
    """
    for escolha, item in opcoes.items():
        print(f'{escolha}. {item.upper()}')
    while True:
        op = input('>>> ')
        if op in opcoes:
            break
        else:
            print('Opção inválida')

    return op


def imprimir_livros(livros):
    """Realiza a listagem e impressão dos livros disponíveis."""
    rows = [list(l) + [l.disponiveis] for l in livros]
    headers = database.Livro._columns + ['disponíveis']
    print(tabulate(rows, headers, 'psql'))


def selecionar_usuario():
    """Seleciona um usuário por nome ou matrícula."""
    query = input("Pesquise por nome ou matrícula: ")
    usuarios = database.Usuario.search(query, ['nome'])
    if not usuarios:
        print("Nenhum usuário encontrado!")
        return selecionar_usuario()
    usuarios_map = {str(idx+1): u for idx, u in enumerate(usuarios)}
    usuarios_enum = {k: sumario_usuario(u)
                     for k, u in usuarios_map.items()}
    print("== USUÁRIOS")
    print("   matrícula / nome")
    op = menu_enumeracao(usuarios_enum)
    return usuarios_map[op]


def selecionar_livro():
    """Realiza a seleção de um livro mostrado a partir de uma listagem."""
    query = input("Pesquise por isbn, título, editora, categoria ou ano: ")
    livros = database.Livro.search(query, ['titulo', 'editora',
                                           'ano', 'categoria'])
    if not livros:
        print("Nenhum livro encontrado!")
        return selecionar_livro()
    livros_map = {str(idx+1): u for idx, u in enumerate(livros)}
    livros_enum = {k: sumario_livro(l)
                   for k, l in livros_map.items()}
    print("== LIVROS")
    print("   isbn / titulo / editora / ano / categoria / disponíveis")
    op = menu_enumeracao(livros_enum)
    return livros_map[op]
