"""
Arquivo que liga a API.
Rode com "python run.py" e ela sobe em http://localhost:5000.
"""
from app import create_app
app = create_app()
if __name__ == "__main__":
#Desligar debug no servidor
    app.run(debug=True, port=5000)