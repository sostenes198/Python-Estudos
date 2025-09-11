# main.py
from app_factory import create_app
from extensions import db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("Banco de dados criado!")
    app.run(debug=True)
