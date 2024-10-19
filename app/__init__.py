from flask import Flask 
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# set to the name of the module
app = Flask(__name__)
app.config.from_object(Config)

# Creating an instance of all the flask-extension
db = SQLAlchemy(app) # db object 
migrate = Migrate(app, db) # databse migration engine
login = LoginManager(app)
login.login_view = 'login' # name of the view function that handles login

from app import routes, models, errors