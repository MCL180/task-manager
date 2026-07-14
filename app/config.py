from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "mysql+pymysql://root:taskmanager123@localhost:3306/task_manager"
    jwt_secret_key: str = "change-me-to-a-random-string-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    qweather_api_key: str = ""
    redis_url: str = "redis://localhost:6379/0"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
