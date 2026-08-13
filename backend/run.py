"""
Ponto de entrada da aplicação TabFlower.

Execute com:  python run.py
A API sobe em http://localhost:5000
"""

from app import create_app

app = create_app()

if __name__ == "__main__":
    # debug=True e o modo de desenvolvimento: ele recarrega a API sozinha a
    # cada arquivo salvo e mostra o erro completo na tela, o que economiza
    # muito tempo enquanto o sistema esta sendo construido.
    #
    # Num servidor de verdade isso NAO pode ficar ligado. O modo debug
    # publica junto o console interativo do Werkzeug: quem abrir a pagina de
    # erro consegue digitar comandos Python e executa-los dentro do servidor,
    # com acesso ao banco e aos arquivos. Aqui e aceitavel porque a API roda
    # em localhost, na maquina do proprio aluno.
    app.run(debug=True, port=5000)
