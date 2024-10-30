from flask import Blueprint

bp = Blueprint('errors', __name__)

# to register the handlers with Blueprint
from app.errors import handlers