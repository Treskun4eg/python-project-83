from urllib.parse import urlparse
import validators


def extract_domain_and_normalize(url):
    parse_url = urlparse(url)
    normalized_url = parse_url.scheme + '://' + parse_url.netloc
    return normalized_url


def validation_url(url):
    errors = {}
    get_a_domain = extract_domain_and_normalize(url)
    url_valid = validators.url(url)
    if not url_valid and len(get_a_domain) > 255:
        errors["VarcharERROR1"] = "URL превышает 255 символов"
    if not url_valid and len(url) == 0:
        errors["VarcharERROR2"] = "Некорректный URL"
        errors["VarcharERROR3"] = "URL обязателен"
    if not url_valid and 255 > len(url) > 0:
        errors["VarcharERROR2"] = "Некорректный URL"
    return errors
