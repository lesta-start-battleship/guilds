# инструкция по работе с файлом "Makefile" – https://bytes.usc.edu/cs104/wiki/makefile/

# обновление сборки Docker-контейнера
build:
	docker compose build

# генерация документации
docs-html:
	docker compose run --no-deps --workdir /docs lesta-games-app /bin/bash -c "make html"

# запуск форматирования кода
format:
	docker compose run --no-deps --workdir / lesta-games-app /bin/bash -c "black src docs/source/*.py; isort --profile black src docs/source/*.py"

# запуск статического анализа кода (выявление ошибок типов и форматирования кода)
lint:
	docker compose run --no-deps --workdir / lesta-games-app /bin/bash -c "pylint src; flake8 src; mypy src; black --check src"



# запуск всех функций поддержки качества кода
all: format lint
