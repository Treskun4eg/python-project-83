from psycopg2 import extras
from page_analyzer.validator import extract_domain_and_normalize
from datetime import date


def get_urls(connect):
    with connect.cursor(cursor_factory=extras.NamedTupleCursor) as cursor:
        cursor.execute("""SELECT id, name, created_at
                            FROM urls
                            ORDER BY created_at DESC,
                            id DESC;""")
        return cursor.fetchall()


def get_last_URL_check(connect):
    with connect.cursor(cursor_factory=extras.NamedTupleCursor) as cursor:
        cursor.execute("""SELECT url_id, MAX(created_at), status_code
                        FROM url_checks GROUP BY url_id, status_code;""")
        return cursor.fetchall()


def created_url(url_name, connect):
    date_today = date.today()
    normalized_url = extract_domain_and_normalize(url_name)
    with connect.cursor(cursor_factory=extras.NamedTupleCursor) as cursor:
        cursor.execute(
            """INSERT INTO urls (name, created_at)
            VALUES (%s, %s);""",
            (normalized_url, date_today)
        )


def get_url_id_by_name(url_name, connect):
    normalized_url = extract_domain_and_normalize(url_name)
    with connect.cursor(cursor_factory=extras.NamedTupleCursor) as cursor:
        cursor.execute("""SELECT id FROM urls WHERE name = %s;""",
                       (normalized_url,))
        return cursor.fetchone()


def get_url_by_id(id, connect):
    with connect.cursor(cursor_factory=extras.NamedTupleCursor) as cursor:
        cursor.execute("""SELECT id, name, created_at
                                FROM urls WHERE id = %s;""",
                       (id,))
        return cursor.fetchone()


def get_url_checks_by_url_id(url_id, connect):
    with connect.cursor(cursor_factory=extras.NamedTupleCursor) as cursor:
        cursor.execute("""SELECT
                              id,
                              url_id,
                              status_code,
                              h1,
                              title,
                              description,
                              created_at
                          FROM
                              url_checks
                          WHERE
                              url_id = %s;""",
                       (url_id,))
        return cursor.fetchall()


def created_url_checks(url_id,
                       status_code,
                       h1,
                       title,
                       description,
                       date_today,
                       connect):
    with connect.cursor(cursor_factory=extras.NamedTupleCursor) as cursor:
        cursor.execute(
                """INSERT INTO url_checks (url_id,
                                            status_code,
                                            h1,
                                            title,
                                            description,
                                            created_at)
                   VALUES (%s, %s, %s, %s, %s, %s);""",
                (url_id, status_code, h1, title, description, date_today)
            )
