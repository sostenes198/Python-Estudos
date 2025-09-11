class Config:
    SECRET_KEY = 'chave_secreta'
    CACHE_TYPE = 'simple'
    SWAGGER = {
        'title': 'Catálogo de receitas',
        'uiversion': 3,
    }
    SQLALCHEMY_DATABASE_URI = 'sqlite:///recipes.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = 'chave_secreta_jwt'