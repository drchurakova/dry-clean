# -*- coding: utf-8 -*-
from my_app import app


@app.route('/')
def index():
    return 'Запустилось!'
