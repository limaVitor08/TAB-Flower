"""
Extensões compartilhadas da aplicação.

Aqui vive a Única instância do SQLAlchemy do projeto inteiro. Todas as
Models, todos os Repositories e todos os Services importam este mesmo
objeto "db". E o padrão Singleton aplicado ao acesso ao banco: um único
ponto de conexão, reutilizado por toda a aplicação.

    from extensions import db

Nunca crie um segundo SQLAlchemy() em outro arquivo. Se isso acontecer,
a aplicação passa a ter duas conexoes independentes e as transações
deixam de funcionar corretamente.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
