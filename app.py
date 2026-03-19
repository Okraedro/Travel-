from flask import Flask
from models import db

def create_app():
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///travel_diary.db'
    app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
    app.config['UPLOAD_FOLDER'] = 'static/uploads'

    # Инициализируем расширения
    db.init_app(app)

    # Регистрируем маршруты (импортируем после создания app)
    from routes import *

    return app

app = create_app()

# Создаём таблицы БД при первом запуске
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)

