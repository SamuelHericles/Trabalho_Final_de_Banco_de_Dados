# coding: utf-8

import os

"""O arquivo build.py gera o executável embarcado para fácil utilização.

Este executável será encapsulado com o interpretador Python, as
bibliotecas usadas nesse projeto e o código-fonte do projeto em si. De
tal maneira que seja portátil na máquina de um usuário mesmo que ele
não tenha instalado o interpretador Python ou mesmo as bibliotecas
utilizadas no projeto (como o driver do MySQL).

Embora quase todo sistema decente exista um interpretador Python, em
especial o sistema Windows não vem com um interpretador.
"""

os.system("pyinstaller teca.spec")
