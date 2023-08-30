install:
	poetry install

build:
	poetry build

build_sh:
	./build.sh

test-coverage:
	poetry run pytest --cov=page_analyzer tests/ --cov-report xml

publish:
	poetry publish --dry-run

package-install:
	python3 -m pip install --user dist/*.whl

make lint:
	poetry run flake8 page_analyzer

selfcheck:
	poetry check

reinstal:
	pip install --user --force-reinstall dist/*.whl
.PHONI: install build publish reinstall selfcheck check

dev:
	poetry run flask --app page_analyzer:app --debug run

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app
.PHONI: install build publish reinstall selfcheck check