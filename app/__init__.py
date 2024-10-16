from flask import Flask 
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# set to the name of the module
app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app) # db object 
migrate = Migrate(app, db) # databse migration engine

from app import routes, models