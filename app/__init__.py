from flask import Flask 

# set to the name of the module
app = Flask(__name__)

from app import routes