import os

class Config:
    SECRET_KEY = 'ini-adalah-kunci-rahasia-pabrik-sangat-aman'
    # Ini artinya kita pakai SQLite, file databasenya nanti otomatis bernama 'teknik_pabrik.db'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///teknik_pabrik.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False