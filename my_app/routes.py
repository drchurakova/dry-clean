# -*- coding: utf-8 -*-
from my_app import app, conn
from flask import render_template, flash, redirect, url_for, request
from my_app.forms import LoginForm, NewAccountClientForm, NewAccountEmployeeForm, ChangePasswordForm, ActiveOrdersForm, NewOrderForm, NewGarmentForm, ChangeCleaningStepForm, ReadyOrdersForm, ChoiceChangeAccountEmployeeForm, ChangeAccountEmployeeForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import logout_user, login_required, login_user, current_user
from my_app.models import load_user, User
from datetime import date
import os

cursor = conn.cursor()


id_order = None
id_item = None
inn = None


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Главная страница')


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
        if current_user.is_client:
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
        if not current_user.is_authenticated:
            cursor.execute('select id from account where login = %s;', (form.login.data,))
            user = cursor.fetchone()
            if user is not None:
                login_user(load_user(user[0]))
                flash('Вы успешно зарегистрировались!')
                cursor.execute('select id from order_of_service where phone_client = %s;', (current_user.phone,))
                orders = cursor.fetchall()
                if orders:
                    for order in orders:
                        cursor.execute('update order_of_service set id_client = %s where id = %s;', (current_user.id, order[0],))
                        conn.commit()
                    flash('Теперь к вашему аккаунту привязаны все Ваши заказы!')
                return redirect(url_for('account'))
        else:
            flash('Вы успешно зарегистрировали новый аккаунт для {}'.format(form.fio.data))
            return redirect(url_for('account'))
    return render_template('create_account.html', title='Регистрация', form=form)


@app.route('/account', methods=['GET', 'POST'])
@login_required
def account():
    form = None
    if not current_user.is_client:
        form = ChoiceChangeAccountEmployeeForm()
        if form.validate_on_submit():
            global inn
            inn = form.inn.data
            cursor.execute('select id from account where inn = %s;', (inn,))
            id_for_inn = cursor.fetchone()
            if id_for_inn is None:
                flash('Аккаунта с данным ИНН не существует.')
                return redirect(url_for('account'))
            else:
                return redirect(url_for('change_account'))
    return render_template('account.html', title='Аккаунт', form=form)


@app.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if check_password_hash(current_user.password_hash, form.password_old.data) and form.password_new.data == form.password_new_replay.data:
            cursor.execute('update account set password_hash = %s where id = %s;', (generate_password_hash(form.password_new.data), current_user.id,))
            conn.commit()
            flash('Пароль был успешно изменен.')
            return redirect(url_for('account'))
        else:
            flash('Старый пароль введен неверно или новые пароли не совпадают!')
            return redirect(url_for('change_password'))
    return render_template('change_password.html', title='Изменение пароля', form=form)


@app.route('/change_account', methods=['GET', 'POST'])
@login_required
def change_account():
    if current_user.is_client:
        flash('У вас нет власти!')
        return redirect(url_for('account'))
    form = ChangeAccountEmployeeForm()
    global inn
    if form.validate_on_submit():
        cursor.execute('select id from account where (inn = %s or phone = %s or login = %s) and inn != %s;', (form.inn.data, form.phone.data, form.login.data, inn,))
        change_user_fake = cursor.fetchone()
        if change_user_fake is None:
            cursor.execute('update account set login = %s, inn = %s, fio = %s, id_job = %s, salary = %s, phone = %s where inn = %s;', (form.login.data, form.inn.data, form.fio.data, form.id_job.data, form.salary.data, form.phone.data, inn,))
            conn.commit()
            flash('Данные изменены!')
            inn = None
            return redirect(url_for('account'))
        else:
            flash('Данный инн, телефон или логин уже заняты!')
            return redirect(url_for('change_account'))
    elif request.method == 'GET':
        cursor.execute('select * from account where inn = %s;', (inn,))
        change_user = cursor.fetchone()
        form.login.data = change_user[1]
        form.inn.data = change_user[3]
        form.fio.data = change_user[4]
        form.id_job.data = change_user[5]
        form.salary.data = change_user[6]
        form.phone.data = change_user[7]
    return render_template('change_account.html', title='Изменение аккаунта', form=form)


@app.route('/orders_active', methods=['GET', 'POST'])
@login_required
def orders_active():
    form = ActiveOrdersForm()
    if current_user.is_client:
        cursor.execute('select * from order_of_service where id_client = %s and date2 is null order by id desc;', (current_user.id,))
    else:
        cursor.execute('select * from order_of_service where id_employee = %s and date2 is null order by id desc;', (current_user.id,))
    orders = cursor.fetchall()
    cursor.execute('select fio from account where id != 1 order by id asc;')
    account = cursor.fetchall()
    if current_user.is_client:
        cursor.execute('select * from garment where id_order in (select id from order_of_service where id_client = %s and date2 is null) order by id asc;', (current_user.id,))
    else:
        cursor.execute('select * from garment where id_order in (select id from order_of_service where id_employee = %s and date2 is null) order by id asc;', (current_user.id,))
    garments = cursor.fetchall()
    cursor.execute('select title from material;')
    material = cursor.fetchall()
    cursor.execute('select title from cleaning_step;')
    step = cursor.fetchall()
    cursor.execute('select title from category_of_item;')
    category = cursor.fetchall()
    if form.validate_on_submit():
        global id_order
        global id_item
        id_order = form.id_order.data
        id_item = form.id_item.data
        return redirect(url_for('change_cleaning_step'))
    return render_template('orders_active.html', title='Активные заказы', form=form, orders=orders, account=account, garments=garments, material=material, step=step, category=category)


@app.route('/orders_ready', methods=['GET', 'POST'])
@login_required
def orders_ready():
    form = ReadyOrdersForm()
    if current_user.is_client:
        cursor.execute('select * from order_of_service where id_client = %s and date2 is not null and date3 is null order by id desc;', (current_user.id,))
    else:
        cursor.execute('select * from order_of_service where id_employee = %s and date2 is not null and date3 is null order by id desc;', (current_user.id,))
    orders = cursor.fetchall()
    cursor.execute('select fio from account where id != 1 order by id asc;')
    account = cursor.fetchall()
    if current_user.is_client:
        cursor.execute('select * from garment where id_order in (select id from order_of_service where id_client = %s and date2 is not null and date3 is null) order by id asc;', (current_user.id,))
    else:
        cursor.execute('select * from garment where id_order in (select id from order_of_service where id_employee = %s and date2 is not null and date3 is null) order by id asc;', (current_user.id,))
    garments = cursor.fetchall()
    cursor.execute('select title from material;')
    material = cursor.fetchall()
    cursor.execute('select title from cleaning_step;')
    step = cursor.fetchall()
    cursor.execute('select title from category_of_item;')
    category = cursor.fetchall()
    if form.validate_on_submit():
        global id_order
        id_order = form.id_order.data
        cursor.execute('update order_of_service set date3 = %s where id = %s;', (date.today(), id_order,))
        conn.commit()
        flash('Заказ отдан клиенту!')
        return redirect(url_for('orders_my'))
    return render_template('orders_ready.html', title='Готовые заказы', form=form, orders=orders, account=account, garments=garments, material=material, step=step, category=category)


@app.route('/orders_my')
@login_required
def orders_my():
    if current_user.is_client:
        cursor.execute('select * from order_of_service where id_client = %s order by id desc;', (current_user.id,))
    else:
        cursor.execute('select * from order_of_service where id_employee = %s order by id desc;', (current_user.id,))
    orders = cursor.fetchall()
    cursor.execute('select fio from account where id != 1 order by id asc;')
    account = cursor.fetchall()
    if current_user.is_client:
        cursor.execute('select * from garment where id_order in (select id from order_of_service where id_client = %s) order by id asc;', (current_user.id,))
    else:
        cursor.execute('select * from garment where id_order in (select id from order_of_service where id_employee = %s) order by id asc;', (current_user.id,))
    garments = cursor.fetchall()
    cursor.execute('select title from material;')
    material = cursor.fetchall()
    cursor.execute('select title from cleaning_step;')
    step = cursor.fetchall()
    cursor.execute('select title from category_of_item;')
    category = cursor.fetchall()
    return render_template('orders_my.html', title='Мои заказы', orders=orders, account=account, garments=garments, material=material, step=step, category=category)


@app.route('/orders_all')
@login_required
def orders_all():
    if current_user.is_client:
        flash('Вы не сотрудник химчистки!')
        return redirect(url_for('account'))
    cursor.execute('select * from order_of_service order by id desc;')
    orders = cursor.fetchall()
    cursor.execute('select fio from account where id != 1 order by id asc;')
    account = cursor.fetchall()
    cursor.execute('select * from garment order by id asc;')
    garments = cursor.fetchall()
    cursor.execute('select title from material;')
    material = cursor.fetchall()
    cursor.execute('select title from cleaning_step;')
    step = cursor.fetchall()
    cursor.execute('select title from category_of_item;')
    category = cursor.fetchall()
    return render_template('orders_all.html', title='Все заказы', orders=orders, account=account, garments=garments, material=material, step=step, category=category)


@app.route('/orders_new', methods=['GET', 'POST'])
@login_required
def orders_new():
    if current_user.is_client:
        flash('Вы не сотрудник химчистки!')
        return redirect(url_for('account'))
    global id_order
    id_order = None
    form = NewOrderForm()
    if form.validate_on_submit():
        cursor.execute('select id from account where phone = %s;', (form.phone_client.data,))
        id_client = cursor.fetchone()
        if id_client is None:
            id_client = 1
        cursor.execute('insert into order_of_service (date1, id_client, id_employee, phone_client) values (%s, %s, %s, %s);', (date.today(), id_client, current_user.id, form.phone_client.data,))
        cursor.execute('select max(id) from order_of_service where phone_client = %s;', (form.phone_client.data,))
        id_order = cursor.fetchone()
        if id_order is not None:
            id_order = id_order[0]
        conn.commit()
        flash('Заказ сформирован, добавьте вещи!')
        return redirect(url_for('orders_garment_new'))
    return render_template('orders_new.html', title='Новый заказ', form=form)


@app.route('/orders_garment_new', methods=['GET', 'POST'])
@login_required
def orders_garment_new():
    if current_user.is_client:
        flash('Вы не сотрудник химчистки!')
        return redirect(url_for('account'))
    global id_order
    if id_order is None:
        flash('Нет активного заказа!')
        return redirect(url_for('orders_new'))
    form = NewGarmentForm()
    if form.validate_on_submit():
        cursor.execute('insert into garment (id_order, id_material, id_step, id_categories) values (%s, %s, 2, %s);', (id_order, form.id_material.data, form.id_category.data,))
        conn.commit()
        if form.end_garment.data:
            cursor.execute('select sum(category_of_item.price) from garment inner join category_of_item on garment.id_categories = category_of_item.id where garment.id_order = %s;', (id_order,))
            price = cursor.fetchone()
            cursor.execute('update order_of_service set price = %s where id = %s;', (price[0], id_order,))
            conn.commit()
            id_order = None
            flash('Последняя вещь добавлена к заказу!')
            return redirect(url_for('orders_active'))
        flash('Вещь добавлена к заказу!')
        return redirect(url_for('orders_garment_new'))
    return render_template('orders_garment_new.html', title='Добавление вещи в заказ', form=form)


@app.route('/change_cleaning_step', methods=['GET', 'POST'])
@login_required
def change_cleaning_step():
    if current_user.is_client:
        flash('Вы не сотрудник химчистки!')
        return redirect(url_for('account'))
    form = ChangeCleaningStepForm()
    global id_order
    global id_item
    if form.validate_on_submit():
        cursor.execute('update garment set id_step = %s where id = %s;', (form.id_step.data, id_item,))
        conn.commit()
        flash('Этап чистки вещи изменен.')
        if form.id_step.data == 11:
            cursor.execute('select category_of_item.price + category_of_item.compensation from garment inner join category_of_item on garment.id_categories = category_of_item.id where garment.id = %s;', (id_item,))
            compensation = cursor.fetchone()
            cursor.execute('update order_of_service set compensation = %s where id = %s;', (compensation[0], id_order,))
            flash('В заказ добавлена компенсация за данную вещь.')
        if form.id_step.data >= 10:
            cursor.execute('select id from garment where id_step < 10 and id_order = %s;', (id_order,))
            orders = cursor.fetchone()
            if orders is None:
                cursor.execute('update order_of_service set date2 = %s where id = %s;', (date.today(), id_order,))
                flash('Данный заказ теперь готов.')
                return redirect(url_for('orders_ready'))
        id_item = None
        id_order = None
        return redirect(url_for('orders_active'))
    elif request.method == 'GET':
        cursor.execute('select id_step from garment where id = %s;', (id_item,))
        id_step = cursor.fetchone()
        form.id_step.data = id_step[0]
    return render_template('change_cleaning_step.html', title='Изменение этапа чистки', form=form)

