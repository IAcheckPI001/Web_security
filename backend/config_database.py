class Config_database:
    def __init__(self, SECRET_KEY, SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS ):
        self.SECRET_KEY = SECRET_KEY
        self.SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI
        self.SQLALCHEMY_TRACK_MODIFICATIONS  = SQLALCHEMY_TRACK_MODIFICATIONS

