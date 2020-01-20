# -*- coding: utf-8 -*-
from my_app import app, conn
from flask_login import LoginManager, UserMixin


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Для просмотра данной страницы требуется войти в аккаунт."


class User(UserMixin):
    def __init__(self, id, login, password_hash, inn, fio, id_job, salary, phone):
        self.id = id
        self.login = login
        self.password_hash = password_hash
        self.inn = inn
        self.fio = fio
        self.id_job = id_job
        self.salary = salary
        self.phone = phone
        if inn is None:
            self.is_client = True
        else:
            self.is_client = False

    def __repr__(self):
        return '<User {}>'.format(self.login)


@login_manager.user_loader
def load_user(user_id):
    cursor = conn.cursor()
    cursor.execute("select * from account where id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()
    if user:
        return User(user[0], user[1], user[2], user[3], user[4], user[5], user[6], user[7])
    else:
        return None
