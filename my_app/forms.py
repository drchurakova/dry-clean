from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, DateField, SubmitField, IntegerField, SelectField, validators
from my_app import app, conn


class LoginForm(FlaskForm):
    login = StringField('Логин', [validators.DataRequired()])
    password = PasswordField('Пароль', [validators.DataRequired()])
    remember_me = BooleanField('Запомнить')
    submit = SubmitField('Войти')


class NewAccountClientForm(FlaskForm):
    login = StringField('Логин', [validators.DataRequired()])
    password = PasswordField('Пароль', [validators.DataRequired()])
    password_replay = PasswordField('Повторите пароль', [validators.DataRequired()])
    fio = StringField('ФИО', [validators.DataRequired()])
    phone = IntegerField('Номер телефона', [validators.NumberRange(min=89000000000, max=89999999999)])
    submit = SubmitField('Зарегистрироваться')


class NewAccountEmployeeForm(FlaskForm):
    login = StringField('Логин', [validators.DataRequired()])
    password = PasswordField('Пароль', [validators.DataRequired()])
    inn = IntegerField('ИНН', [validators.DataRequired(), validators.NumberRange(min=100000000000, max=999999999999)])
    fio = StringField('ФИО', [validators.DataRequired()])
    cursor = conn.cursor()
    cursor.execute("select * from job_title")
    job_title = cursor.fetchall()
    cursor.close()
    id_job = SelectField('Должность', choices=job_title, coerce=int)
    salary = IntegerField('Зарплата', [validators.DataRequired()])
    phone = IntegerField('Номер телефона', [validators.NumberRange(min=89000000000, max=89999999999)])
    submit = SubmitField('Зарегистрировать')

class ChoiceChangeAccountEmployeeForm(FlaskForm):
    inn = IntegerField('ИНН', [validators.DataRequired(), validators.NumberRange(min=100000000000, max=999999999999)])
    submit = SubmitField('Найти')

class ChangeAccountEmployeeForm(FlaskForm):
    login = StringField('Логин', [validators.DataRequired()])
    inn = IntegerField('ИНН', [validators.DataRequired(), validators.NumberRange(min=100000000000, max=999999999999)])
    fio = StringField('ФИО', [validators.DataRequired()])
    cursor = conn.cursor()
    cursor.execute("select * from job_title")
    job_title = cursor.fetchall()
    cursor.close()
    id_job = SelectField('Должность', choices=job_title, coerce=int)
    salary = IntegerField('Зарплата', [validators.DataRequired()])
    phone = IntegerField('Номер телефона', [validators.NumberRange(min=89000000000, max=89999999999)])
    submit = SubmitField('Изменить')

class ChangePasswordForm(FlaskForm):
    password_old = PasswordField('Старый пароль', [validators.DataRequired()])
    password_new = PasswordField('Новый пароль', [validators.DataRequired()])
    password_new_replay = PasswordField('Повторите новый пароль', [validators.DataRequired()])
    submit = SubmitField('Изменить')


class ActiveOrdersForm(FlaskForm):
    id_order = StringField('id_order')
    id_item = StringField('id_item')
    submit = SubmitField('Нашли')


class ReadyOrdersForm(FlaskForm):
    id_order = StringField('id_order')
    submit = SubmitField('Нашли')


class NewOrderForm(FlaskForm):
    phone_client = IntegerField('Номер телефона клиента', [validators.NumberRange(min=89000000000, max=89999999999)])
    submit = SubmitField('Продолжить')


class NewGarmentForm(FlaskForm):
    cursor = conn.cursor()
    cursor.execute("select * from material")
    material = cursor.fetchall()
    id_material = SelectField('Материал', choices=material, coerce=int)
    cursor.execute("select id, title from category_of_item")
    category_of_item = cursor.fetchall()
    id_category = SelectField('Категория вещи', choices=category_of_item, coerce=int)
    cursor.close()
    end_garment = BooleanField('Последняя вещь')
    submit = SubmitField('Добавить')


class ChangeCleaningStepForm(FlaskForm):
    cursor = conn.cursor()
    cursor.execute("select * from cleaning_step")
    cleaning_step = cursor.fetchall()
    cursor.close()
    id_step = SelectField('Этап чистки', choices=cleaning_step, coerce=int)
    submit = SubmitField('Сменить')

