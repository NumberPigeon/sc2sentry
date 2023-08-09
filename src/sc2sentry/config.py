from dynaconf import Dynaconf

settings = Dynaconf(
    envvar_prefix="SC2SENTRY",
    settings_files=["settings.toml", ".secrets.toml"],
)


db_url = f"{settings.database.dialect}+{settings.database.api}://{settings.database.user}:{settings.database.password}@{settings.database.host}:{settings.database.port}/{settings.database.name}"
settings.database.url = db_url
