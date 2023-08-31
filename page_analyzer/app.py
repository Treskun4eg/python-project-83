from flask import (
    Flask,
    render_template,
    request,
    redirect,
    flash,
    url_for,
    get_flashed_messages
)
import os
import psycopg2
from urllib.parse import urlparse
from datetime import date
import validators
from dotenv import load_dotenv


load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
connect = psycopg2.connect(DATABASE_URL)
connect.autocommit = True


def extract_domain_and_normalize(data):
    url = data['url']
    parse_url = urlparse(url)
    normalized_url = parse_url.scheme + '://' + parse_url.netloc
    return normalized_url


def validation_url(data):
    errors = {}
    url = data['url']
    get_a_domain = extract_domain_and_normalize(data)
    url_valid = validators.url(url)
    if not url_valid and len(get_a_domain) > 255:
        errors["VarcharERROR1"] = "URL превышает 255 символов"
    if not url_valid and len(url) == 0:
        errors["VarcharERROR2"] = "Некорректный URL"
        errors["VarcharERROR3"] = "URL обязателен"
    if not url_valid and 255 > len(url) > 0:
        errors["VarcharERROR2"] = "Некорректный URL"
    return errors


@app.route('/')
def index():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)


@app.get('/urls')
def get_urls():
    with connect.cursor() as cursor:
        try:
            cursor.execute("""SELECT * FROM urls
                            ORDER BY created_at DESC, id DESC;""")
            records = cursor.fetchall()
        except Exception as err:
            print(err)
    return render_template('urls.html', records=records)


@app.post('/urls')
def add_url():

    data = request.form.to_dict()
    errors = validation_url(data)
    data_today = date.today()

    if errors:
        for key, value in errors.items():
            flash(value, key)
        return redirect(url_for('index'))

    normalized_url = extract_domain_and_normalize(data)

    with connect.cursor() as cursor:

        try:
            cursor.execute(
                """INSERT INTO urls (name, created_at)
                VALUES (%s, %s);""",
                (normalized_url, data_today)
            )
            record = cursor.fetchone()
            print(record)
            flash('Страница успешно добавлена', 'Успех')
            return render_template(url_for('get_url_id'), record=record)

        except Exception as err:
            cursor.execute("""SELECT id FROM urls WHERE name = %s;""",
                           (normalized_url,))
            record = cursor.fetchone()
            flash('Страница уже существует', 'Повторение')
            print(err)
            print(record)
            return redirect(url_for('get_url_id', id=record[0]))


@app.get('/urls/<int:id>')
def get_url_id(id):
    with connect.cursor() as cursor:
        cursor.execute("""SELECT id, name, created_at
                        FROM urls WHERE id = %s;""",
                       (id,))
        record = cursor.fetchone()
    messages = get_flashed_messages(with_categories=True)
    return render_template('url_id.html', record=record, messages=messages)
