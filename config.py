import os 
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config:
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
								"sqlite:///" + os.path.join(basedir, 'app.db')
	MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
	MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
	MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
	ADMINS = ['your-email@example.com']
	POSTS_PER_PAGE = 3
	LANGUAGES = ['en', 'es']