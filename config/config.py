from urllib.parse import quote


class Config():
    SQLALCHEMY_POOL_SIZE = 10
    SQLALCHEMY_MAX_OVERFLOW = 20
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:123@localhost:5432/remote"
    SQLALCHEMY_TRACK_MODIFICATIONS = True
