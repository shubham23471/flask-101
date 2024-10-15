from flask import Flask 
from config import Config

# set to the name of the module
app = Flask(__name__)
app.config.from_object(Config)
from app import routes