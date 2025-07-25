# Сервис guild

Сервис guild .

## Версия приложения

V 0.0.1

## Требования:

Установите необходимое программное обеспечение:

1. [Docker Desktop](https://www.docker.com).
2. [Git](https://github.com/git-guides/install-git).
3. [PyCharm](https://www.jetbrains.com/ru-ru/pycharm/download) (optional).

## Описание структуры проекта

<details>
<summary>Дерево проекта</summary>

```
main-directory-name/
│
├── app/                      # проект
│   ├── schemas/              # Модуль в котором хранятся схемы Pydantic для обработки данных
│   ├── services/             # Сервисный слой для бизнесс логики приложения
│   ├── alembic/              # Директория с результатами миграций моделей 
│   │   ├── versions/         # Директория с миграциями
│   │   ├── env.py            # Настройки Alembic
│   │   └── ...
│   ├── db/                   # Пакет с моделями проекта и подключением к БД
│   │   ├── models/
│   │   │     └── guild.py          # Модуль в котором описаны модели приложения
│   │   ├── __init__.py
│   │   └── database.py       # Модуль с настройками подключения к БД
│   ├── alembic.ini           # ini фвйл настроек Alembic
│   ├── main.py               # Основной модуль для запуска приложения
│   └── settings.py           # Настройки приложения через Pydantic
├── tests/                    # Директория с тестами проекта
├── Dockerfile
├── docker-compose.yml        # Основной Docker Compose файл
├── .env.sample               # Файл для настроек переменных окружения
├── .gitignore                # Файл gitignore служит для игнорирования файлов для git
├── .pylintrc                 # 
├── black.toml                # 
├── LICENSE                   # Файл лицензии
├── Makefile                  # Makefile Файл приложения для удобства сборки проекта и других манипуляций с проектом
├── pytest.ini                # Файл настройки pytest
├── requirements.txt          # Файл зависимостей проекта
├── setup.cfg                 # Файл установки настроек линтеров
└── README.md
```

</details>

## Конфигурируемые параметры

Все конфигурируемые параметры находятся в файле .env.sample и разделены по блокам

## Установка

Клонируйте репозиторий на ваш компьютер.

1. Для настройки приложения скопируйте файл `.env.sample` в файл `.env`:
   
   ```shell
   cp .env.sample .env
   ```
   
   Этот файл содержит переменные окружения, которые будут использоваться в приложении. Примерный файл `.env.sample`) содержит набор переменных с настройками по умолчанию. Его можно настроить в зависимости от окружения.
2. Постройте контейнер с помощью Docker Compose:
   
   ```shell
   docker compose build
   ```
   
   Эта команда должна быть выполнена из корневой директории, где находится `Dockerfile` .
   Также нужно будет заново построить контейнер, если вы обновили `requirements.txt`.
3. Для корректной работы приложения настройте базу данных. Примените миграции для создания таблиц в базе данных:
   
   ```shell
   docker compose run lesta-games-app alembic upgrade head
   ```
4. Теперь можно запустить проект внутри Docker контейнера:
   
   ```shell
   docker compose up
   ```
   
   Когда контейнеры будут запущены, сервер начнёт работать по адресу [http://0.0.0.0:8010/docs](http://0.0.0.0:8010/docs). Вы можете открыть его в браузере.

## Использование

### Миграции

Для первоначальной настройки функционала миграций выполните команду:

```bash
docker compose exec lesta-games-app alembic init -t async migrations
```

Эта команда создаст директорию с конфигурационными файлами для настройки функционала асинхронных миграций.

Для создания новых миграций, которые обновят таблицы базы данных в соответствии с обновлёнными моделями, выполните команду:

```bash
docker compose run lesta-games-app alembic revision --autogenerate  -m "your description"
```

Чтобы применить созданные миграции, выполните:

```bash
docker compose run lesta-games-app alembic upgrade head
```

### Автоматизированные команды

Проект содержит специальный `Makefile` который предоставляет ярлыки для набора команд:

1. Построить Docker контейнер:
   
   ```shell
   make build
   ```
2. Сгенерировать документацию Sphinx:
   
   ```shell
   make docs-html
   ```
3. Автоформатировать исходный код:
   
   ```shell
   make format
   ```
4. Статический анализ (линтеры):
   
   ```shell
   make lint
   ```
5. Run autoformat, linters and tests in one command:
   
   ```shell
   make all
   ```

Запускайте эти команды из исходной директории, где находится `Makefile`.

## Документация

Проект интегрирован с системой документации [Sphinx](https://www.sphinx-doc.org/en/master/) Она позволяет создавать документацию из исходного кода. Исходный код должен содержать docstring'и в формате [reStructuredText](https://docutils.sourceforge.io/rst.html) .

Чтобы создать HTML документацию, выполните команду из исходной директории, где находится `Makefile`:

```shell
make docs-html
```

После генерации документацию можно открыть из файла `docs/build/html/index.html`.

## License

[MIT](https://choosealicense.com/licenses/mit/)





