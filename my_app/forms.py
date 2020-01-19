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

