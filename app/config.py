from pydantic import HttpUrl, SecretStr, computed_field
from pydantic_settings import BaseSettings
from sqlalchemy import URL


class Settings(BaseSettings):
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str
    DB_USERNAME: str
    DB_PASSWORD: SecretStr
    SQLALCHEMY_ECHO: bool = False

    AUTH_ENDPOINT_URL: HttpUrl
    AUTH_FRONT_ENDPOINT_URL: HttpUrl
    AUTH_CALLBACK_URL: HttpUrl
    AUTH_CLIENT_ID: str
    AUTH_CLIENT_SECRET: SecretStr

    @computed_field
    @property
    def database_url(self) -> URL:
        return URL.create(
            "postgresql+psycopg",
            username=self.DB_USERNAME,
            password=self.DB_PASSWORD.get_secret_value(),
            host=self.DB_HOST,
            port=self.DB_PORT,
            database=self.DB_NAME,
        )

    @computed_field
    @property
    def auth_public_key(self) -> str:
        with open("token_jwt_key.pem") as file:
            return file.read()


def get_settings() -> Settings:
    return Settings()  # type: ignore


settings = get_settings()
