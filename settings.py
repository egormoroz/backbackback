from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str

    @property
    def DATABASE_URL_asyncpg(self):
        return 'postgresql+asyncpg://{user}:{pwd}@{host}:{port}/{db}'.format(
                user=self.DB_USER, pwd=self.DB_PASS, host=self.DB_HOST, 
                port=self.DB_PORT, db=self.DB_NAME)

    @property
    def DATABASE_URL_psycopg(self):
        return 'postgresql+psycopg://{user}:{pwd}@{host}:{port}/{db}'.format(
                user=self.DB_USER, pwd=self.DB_PASS, host=self.DB_HOST, 
                port=self.DB_PORT, db=self.DB_NAME)

    model_config = SettingsConfigDict(env_file='.env')

settings = Settings() # pyright: ignore

