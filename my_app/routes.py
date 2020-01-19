# -*- coding: utf-8 -*-
from my_app import app, conn
from flask import render_template, flash, redirect, url_for, request
from my_app.forms import LoginForm, NewAccountClientForm, NewAccountEmployeeForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import logout_user, login_required, login_user, current_user
from my_app.models import load_user, User
from datetime import date
import os

cursor = conn.cursor()


@app.route('/')
@app.route('/index')
def index():
    return 'Запустилось!'


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash('Вы уже вошли в свой аккаунт!')
        return redirect(url_for('account'))
    form = LoginForm()
    if form.validate_on_submit():
        cursor.execute('select id, password_hash from account where login = %s;', (form.login.data,))
        user = cursor.fetchone()
        if user is None or not check_password_hash(user[1], form.password.data):
            flash('Неверный логин или пароль!')
            return redirect(url_for('login'))
        login_user(load_user(user[0]), remember=form.remember_me.data)
        flash('Вы успешно вошли в аккаунт.')
        return redirect(url_for('account'))
    return render_template('login.html', title='Вход', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из аккаунта.')
    return redirect(url_for('login'))


@app.route('/create_account', methods=['GET', 'POST'])
def create_account():
    if current_user.is_authenticated:
        if current_user.client:
            flash('У вас уже есть аккаунт!')
            return redirect(url_for('account'))
        else:
            form = NewAccountEmployeeForm()
    else:
        form = NewAccountClientForm()
    if form.validate_on_submit():
        cursor.execute('select * from account where login = %s;', (form.login.data,))
        user = cursor.fetchone()
        if user:
            flash('Данный логин занят!')
            return redirect(url_for('create_account'))
        if current_user.is_authenticated:
            cursor.execute('insert into account (login, password_hash, inn, fio, id_job, salary, phone) values (%s, %s, %s, %s, %s, %s, %s);', (form.login.data, generate_password_hash(form.password.data), form.inn.data, form.fio.data, form.id_job.data, form.salary.data, form.phone.data,))
            conn.commit()
        else:
            if form.password.data == form.password_replay.data:
                cursor.execute('insert into account (login, password_hash, fio, id_job, phone) values (%s, %s, %s, 1, %s);', (form.login.data, generate_password_hash(form.password.data), form.fio.data, form.phone.data,))
                conn.commit()
            else:
                flash('Пароли не совпадают!')
                return redirect(url_for('create_account'))
        cursor.execute('select id from account where login = %s;', (form.login.data,))
        user = cursor.fetchone()
        if user is not None:
            login_user(load_user(user[0]))
            flash('Вы успешно зарегистрировались!')
            return redirect(url_for('account'))
    return render_template('create_account.html', title='Регистрация', form=form)


@app.route('/account')
def account():
    return 'Аккаунт!'

