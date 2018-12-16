# coding: utf-8


"""Módulo para listagem das views (visões) no banco de dados.
"""


from teca import term
from teca import database
from tabulate import tabulate


def imprimir_consulta(sql, params=()):
    """Recebe uma consulta SQL e gera uma string formatada como tabela"""
    db = database.Database.connect()
    rows = []
    cursor = db.conn.cursor()
    cursor.execute(sql, params)
    for result in cursor:
        rows.append(result)
    headers = [k[0] for k in cursor.description]
    cursor.close()
    print(tabulate(rows, headers, 'psql'))


def view_livro_ano():
    """Utiliza o método imprimir_consulta que busca no SQL a view."""
    imprimir_consulta('SELECT * FROM view_livro_ano')


def view_livro_categoria():
    """Recebe a views de livro por consulta e pergunta para filtrar por categoria."""
    sql = 'SELECT * FROM view_livro_categoria'
    ask = input('Deseja filtrar por categoria? (y/N) ')
    params = ()
    if ask.lower() == 'y':
        print('Categorias com livro registrado')
        imprimir_consulta('SELECT DISTINCT(nome_categoria) FROM view_livro_categoria')
        cat = input('nome da categoria: ')
        where = " WHERE nome_categoria LIKE %s"
        params = ('%' + cat + '%',)
        sql += where
    imprimir_consulta(sql, params)


def view_livro_editora():
    """Recebe a views da SQL de livro por editora e pergunta para filtar por editora."""
    sql = 'SELECT * FROM view_livro_editora'
    ask = input('Deseja filtrar por editora? (y/N) ')
    params = ()
    if ask.lower() == 'y':
        print('Editoras disponíveis no banco')
        imprimir_consulta('SELECT DISTINCT(editora) FROM livro ORDER BY editora')
        editora = input('editora: ')
        where = " WHERE editora LIKE %s"
        params = ('%' + editora + '%',)
        sql += where
    imprimir_consulta(sql, params)


def view_professor_curso():
    """Lista o professor por curso e pergunta para filtar por curso."""
    sql = 'SELECT * FROM view_professor_curso'
    ask = input('Deseja filtrar por curso? (y/N) ')
    params = ()
    if ask.lower() == 'y':
        print('Cursos com professores')
        cursos = ('SELECT DISTINCT(nome_curso) '
                  'FROM view_professor_curso '
                  'ORDER BY nome_curso')
        imprimir_consulta(cursos)
        curso = input('nome_curso: ')
        where = " WHERE nome_curso LIKE %s"
        params = ('%' + curso + '%',)
        sql += where
    imprimir_consulta(sql, params)


def view_reserva_livro():
    """Lista a reserva por livro, com nome de usuários e reservas.

    É possível optar para filtar por livro. Do contrário todas as reservas
    serão exibidas.
    """
    sql = 'SELECT * FROM view_reserva_livro'
    ask = input('Deseja filtrar por livro? (y/N) ')
    params = ()
    if ask.lower() == 'y':
        print('Livros com reservas')
        livros = ('SELECT DISTINCT(isbn), titulo '
                  'FROM view_reserva_livro '
                  'ORDER BY titulo')
        imprimir_consulta(livros)
        key = input('titulo ou isbn: ')
        key = '%' + key + '%'
        where = " WHERE isbn LIKE %s OR titulo LIKE %s"
        params = (key, key)
        sql += where
    imprimir_consulta(sql, params)


def view_livro_autores():
    """Utiliza o método imprimir_consulta que busca no MySQL a view."""
    imprimir_consulta('SELECT * FROM view_livro_autores')


def tela_views():
    """Realiza a listagem das views."""
    print("== VIEWS ==")
    while True:
        opcoes = {
            '1': 'Listar livros por ano',
            '2': 'Listar livros por categoria',
            '3': 'Listar livros por editora',
            '4': 'Listar livros por autor',
            '5': 'Listar professores por curso',
            '6': 'Listar reservas por livro e usuário',
            '0': 'Sair'
        }

        try:
            op = term.menu_enumeracao(opcoes)
        except KeyboardInterrupt:
            print()  # fix next print on terminal
            break

        try:
            if op == '1':
                view_livro_ano()
            elif op == '2':
                view_livro_categoria()
            elif op == '3':
                view_livro_editora()
            elif op == '4':
                view_livro_autores()
            elif op == '5':
                view_professor_curso()
            elif op == '6':
                view_reserva_livro()
            elif op == '0':
                break
            else:
                print('Não implementado!')

            input("Pressione enter para continuar...")
        except KeyboardInterrupt:
            print("\nOperação interrompida!")
