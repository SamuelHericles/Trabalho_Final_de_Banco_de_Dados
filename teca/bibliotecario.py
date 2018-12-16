#!/usr/bin/env python
# coding: utf-8

"""Módulo responsavel para a tela do usuároi nivel administrdor.

Utiliza as bilbiotecas criadas pela equipe para exibir os livros,
ver reservas, ver empréstimos bem como outras opções exigidas pelo
professor no arquivo do trabalho disponibilizado.
"""

from teca import term
from teca import database
from teca import check
from teca import views
from teca.term import selecionar_livro, selecionar_usuario
from teca.term import sumario_reserva
from teca.term import sumario_emprestimo
from teca.term import sumario_usuario
from teca import usuario


def imprimir_usuario(u):
    """Lê e imprime as informações de usuário.

    Como por exemplo: empréstimos, reservas e dados cadastrais.
    """
    u.senha_hash = '*' * 8
    emps = u.emprestimos
    resv = u.reservas
    extra = u.extra
    print("== INFORMAÇÃO DE USUÁRIO")
    print(u)
    if extra:
        extra._column = [k for k in extra._columns
                         if k not in extra._primary_key]
        print(u.extra)
        if u.tipo in ('aluno', 'professor'):
            print("curso: ", extra.nome_curso)
    print("empréstimos: ", len(emps))
    print("reservas: ", len(resv))
    print("telefones: ", ', '.join([t.numero for t in u.telefones]))

    if emps:
        print("== EMPRÉSTIMOS")
        for idx, e in enumerate(emps):
            print(f"{idx + 1}. {sumario_emprestimo(e)}")
    if resv:
        print("== RESERVAS")
        for idx, r in enumerate(resv):
            print(f"{idx + 1}. {sumario_reserva(r)}")
    print("==================================")


def imprimir_livro(livro):
    """Imprime informações do livro além de informações de sua disponibilidade."""
    print("== INFORMAÇÃO DO LIVRO")
    emprestimos = livro.emprestimos
    reservas = livro.reservas
    print(livro)
    print("categoria: ", livro.categoria)
    print("autores: ", ", ".join([a.nome for a in livro.autores]))
    print("empréstimos: ", len(emprestimos))
    print("reservados: ", len(reservas))
    print("disponíveis: ", livro.disponiveis)

    if len(emprestimos) > 0:
        print("== USUÁRIOS COM EMPRÉSTIMO", )
        for e in database.Emprestimo.filter(isbn=livro.isbn):
            u = database.Usuario.select(e.matricula)
            print("    ", sumario_usuario(u))
    if len(reservas) > 0:
        print("== USUÁRIOS COM RESERVA")
        for e in database.Reserva.filter(isbn=livro.isbn):
            u = database.Usuario.select(e.matricula)
            print("    ", sumario_usuario(u))


def consultar_usuarios():
    """Consulta se a entrada possui informações úteis para pesquisa."""
    u = selecionar_usuario()
    if u:
        imprimir_usuario(u)
    else:
        print("Nenhum usuário encontrado!")


def consultar_livros():
    """Consulta as informações detalhadas de um determinado livro."""
    livro = selecionar_livro()
    imprimir_livro(livro)


def consultar_reservas():
    """Consulta de reservas feitas de um ou mais livros."""
    views.view_reserva_livro()


def consultar_emprestimos():
    """Consulta os empréstimos realizados até o momento."""
    sql = ('SELECT titulo, nome as nome_usuario, data_de_emprestimo, data_de_devolucao '
           'FROM emprestimo '
           'NATURAL JOIN livro '
           'NATURAL JOIN usuario '
           'ORDER BY titulo, data_de_emprestimo')
    views.imprimir_consulta(sql)


def realizar_emprestimo():
    """Realiza o empréstimo obedecendo os privilégios dados aos tipos de usuários."""
    print("Escolha um usuário!")
    usuario = selecionar_usuario()
    livro = selecionar_livro()
    ok = check.emprestimo(usuario, livro)
    if not ok:
        print(ok)
        print("EMPRÉSTIMO NÃO REALIZADO!")
        return None

    emprestimo = usuario.gerar_emprestimo(livro.isbn)
    check_reserva = [r for r in usuario.reservas
                     if livro.isbn == r.isbn]
    if check_reserva:
        print("Usuário possui reserva para esse livro!")
        reserva = check_reserva[0]
        reserva.delete()
        print("RESERVA CONSUMIDA!")

    emprestimo.insert()
    data_de_devolucao = emprestimo.data_de_devolucao.strftime("%d/%m/%Y")
    data_de_emprestimo = emprestimo.data_de_emprestimo.strftime("%d/%m/%Y")
    print("EMPRÉSTIMO REALIZADO!")
    print("DATA DE EMPRÉSTIMO: ", data_de_emprestimo)
    print("DATA MÁXIMA PARA DEVOLUÇÃO: ", data_de_devolucao)


def realizar_reserva():
    """Escolhe um usuário e realiza reserva de um determinado livro."""
    print("Escolha um usuário!")
    u = selecionar_usuario()
    usuario.realizar_reserva(u)


def dar_baixa_emprestimo():
    """Lista os empréstimos de um usuário e realiza a baixa de um em específico."""
    print("Escolha um usuário!")
    u = selecionar_usuario()
    emps = u.emprestimos
    if not emps:
        print("Usuário não possuí empréstimos")
        return None
    print("== EMPRÉSTIMOS: ")
    print("   isbn / título / data de empréstimo")
    emps_map = {str(idx+1): e for idx, e in enumerate(emps)}
    emps_enum = {k: sumario_emprestimo(v)
                 for k, v in emps_map.items()}
    op = term.menu_enumeracao(emps_enum)
    e = emps_map[op]
    e.delete()
    print("DEVOLUÇÃO DO EMPRÉSTIMO REALIZADA!")


def fila_anda():
    """Método para o mecanismo da fila andar."""
    conn = database.Database.connect()
    sql = ("DELETE FROM reserva "
           "WHERE data_contemplado is not null")
    conn.commit(sql)
    instances = database.Livro.select_all()

    for instance in instances:
        isb = instance.isbn
        i = instance.qt_copias - len(instance.emprestimos)
        sql = ("UPDATE reserva "
               "SET data_contemplado = now()"
               "WHERE isbn = %s"
               "ORDER BY data_de_reserva "
               "LIMIT %s")
        params = (isb, i)
        conn.commit(sql, params)
    print("Concluído!")


def tela_bibliotecario():
    """Primeira tela após o login de usuário bibliotecário."""
    print("== TELA DE BIBLIOTECÁRIO ==")
    while True:
        opcoes = {
            '1': 'Consultar usuários',
            '2': 'Consultar livros',
            '3': 'Consultar reservas',
            '4': 'Consultar empréstimos',
            '5': 'Realizar empréstimo',
            '6': 'Realizar reserva',
            '7': 'Dar baixa empréstimo',
            '8': 'Atualizar fila de reserva',
            '0': 'Sair',
        }

        try:
            op = term.menu_enumeracao(opcoes)
        except KeyboardInterrupt:
            print()  # fix next print on terminal
            break

        try:
            if op == '1':
                consultar_usuarios()
            elif op == '2':
                consultar_livros()
            elif op == '3':
                consultar_reservas()
            elif op == '4':
                consultar_emprestimos()
            elif op == '5':
                realizar_emprestimo()
            elif op == '6':
                realizar_reserva()
            elif op == '7':
                dar_baixa_emprestimo()
            elif op == '8':
                fila_anda()
            elif op == '0':
                break
            else:
                print('Não implementado!')

            input("Pressione enter para continuar...")
        except KeyboardInterrupt:
            print("\nOperação interrompida!")


if __name__ == '__main__':
    tela_bibliotecario()
