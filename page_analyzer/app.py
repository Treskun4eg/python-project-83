from flask import (
    Flask,
    render_template,
    request,
    redirect,
    flash,
    url_for,
    get_flashed_messages
)

from page_analyzer.validator import validation_url
from page_analyzer import db
from page_analyzer.get_seo import get_seo

import os
from dotenv import load_dotenv
from datetime import date
import psycopg2
import requests


load_dotenv()
app = Flask(__name__)
TIMEOUT = int(os.getenv('EXTERNAL_REQUEST_TIMEOUT', 30))
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
connect = psycopg2.connect(DATABASE_URL)
connect.autocommit = True


@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)


@app.get('/urls')
def list_urls():
    with connect as conn:
        urls = db.get_urls(conn)
        url_checks = {
            item.url_id: item for item in db.get_last_URL_check(conn)
        }
    return render_template('urls.html',
                           urls=urls,
                           url_checks=url_checks)


@app.post('/urls')
def add_url():

    url_name = request.form.to_dict()
    errors = validation_url(url_name)

    if errors:
        for key, value in errors.items():
            flash(value, key)
        return redirect(url_for('index'))

    with connect as conn:
        url_check = db.get_url_id_by_name(url_name, conn)
        if url_check:
            flash('Страница уже существует', 'Повторение')
            return redirect(url_for('get_url_id', id=url_check.id))
        db.created_url(url_name, conn)
        url_id = db.get_url_id_by_name(url_name, conn)
        flash('Страница успешно добавлена', 'Успех')
        return redirect(url_for('get_url_id', id=url_id.id))


@app.get('/urls/<int:id>')
def get_url_id(id):
    with connect as conn:
        url_info = db.get_url_by_id(id, conn)
        checks_info = db.get_url_checks_by_url_id(id, conn)
        messages = get_flashed_messages(with_categories=True)
        return render_template('url_id.html',
                               url_info=url_info,
                               checks_info=checks_info,
                               messages=messages)


@app.post('/urls/<int:id>/checks')
def check_url(id):
    date_today = date.today()

    with connect as conn:

        url_info = db.get_url_by_id(id, conn)
        try:
            request = requests.get(url_info.name, timeout=TIMEOUT)
            request.raise_for_status()
        except requests.exceptions.RequestException as err:
            flash('Произошла ошибка при проверке', 'Ошибка')
            print(err)
            return redirect(url_for('get_url_id', id=url_info.id))
        status_code = request.status_code
        h1, title, description = get_seo(request.text)
        db.created_url_checks(id,
                              status_code,
                              h1,
                              title,
                              description,
                              date_today,
                              conn)
        flash('Страница успешно проверена', 'Успех')
        return redirect(url_for('get_url_id',
                                id=url_info.id))
