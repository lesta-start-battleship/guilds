import os

from pydantic import BaseModel, Field, PostgresDsn
from pydantic_settings import BaseSettings

from dotenv import load_dotenv
load_dotenv()


SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")

class Project(BaseModel):
    """
    Описание проекта.
    """

    #: название проекта
    title: str = "tfidf  Service"
    #: описание проекта
    description: str = "Сервис tfidf ."
    #: версия релиза
    release_version: str = os.getenv("PROJECT__RELEASE_VERSION")


class Settings(BaseSettings):
    """
    Настройки проекта.
    """

    #: режим отладки
    debug: bool = Field(default=False)
    #: уровень логирования
    log_level: str = Field(default="INFO")
    #: описание проекта
    project: Project = Project()
    #: базовый адрес приложения
    base_url: str = Field(default="http://0.0.0.0:8000")
    #: строка подключения к БД
    database_url: PostgresDsn = Field(
        default=SQLALCHEMY_DATABASE_URL
    )

    secret_key: str = Field(default=os.getenv("SECRET_KEY"))
    algorithm: str = Field(default=os.getenv("ALGORITHM"))
    access_token_expire_minutes: int = Field(default=os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"


# инициализация настроек приложения
settings = Settings()
