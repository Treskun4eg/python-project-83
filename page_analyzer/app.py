from flask import (
    Flask,
    render_template,
    request,
    redirect,
    flash,
    url_for,
    get_flashed_messages
)

from page_analyzer.config import Config

from page_analyzer.validator import validation_url
from page_analyzer import db
from page_analyzer.html import get_seo

from dotenv import load_dotenv
from datetime import date
import requests


load_dotenv()
app = Flask(__name__)
app.config.from_object(Config)


@app.route('/')
def index():
    return render_template('index.html')


@app.get('/urls')
def list_urls():
    with app.config['CONNECT'] as conn:
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
    url = url_name['url']
    errors = validation_url(url)

    if errors:
        for key, value in errors.items():
            flash(value, key)
        return render_template('index.html'), 422

    with app.config['CONNECT'] as conn:
        url_check = db.get_url_id_by_name(url, conn)
        if url_check:
            flash('Страница уже существует', 'Повторение')
            return redirect(url_for('get_url_id', id=url_check.id))
        db.created_url(url, conn)
        url_id = db.get_url_id_by_name(url, conn)
        flash('Страница успешно добавлена', 'Успех')
        return redirect(url_for('get_url_id', id=url_id.id))


@app.get('/urls/<int:id>')
def get_url_id(id):
    with app.config['CONNECT'] as conn:
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

    with app.config['CONNECT'] as conn:

        url_info = db.get_url_by_id(id, conn)
        try:
            request = requests.get(url_info.name, timeout=app.config['TIMEOUT'])
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
