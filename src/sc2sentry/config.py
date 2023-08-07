from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="SC2SENTRY",
    settings_files=["settings.toml", ".secrets.toml"],
)


DB_DIALECT = settings.DB_DIALECT
DB_API = settings.DB_API
DB_HOST = settings.DB_HOST
DB_PORT = settings.DB_PORT
DB_USER = settings.DB_USER
DB_PASSWORD = settings.DB_PASSWORD
DB_NAME = settings.DB_NAME
DB_URL = (
    f"{DB_DIALECT}+{DB_API}://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

settings.DB_URL: str = DB_URL
