from flask import Flask, request, current_app
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import logging
from logging.handlers import SMTPHandler, RotatingFileHandler
import os
from flask_mail import Mail
from flask_moment import Moment
from flask_babel import Babel
from flask_babel import Babel, lazy_gettext as _l

def get_locale():
    "for translation using flask-babel"
    return request.accept_languages.best_match(current_app.config['LANGUAGES'])

# Creating an instance of all the flask-extension
db = SQLAlchemy() # db object 
migrate = Migrate() # databse migration engine
login = LoginManager()
login.login_view = 'auth.login' # name of the view function that handles login
login.login_message = _l('Please log in to access this page.')
# for email support
mail = Mail()
# for transaltion 
moment = Moment()
babel = Babel()


def create_app(config_class=Config):
    # set to the name of the module
    app = Flask(__name__)
    app.config.from_object(Config)

    # init the flask framework
    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    babel.init_app(app)

    # error blueprint
    from app.errors import bp as errors_bp
    app.register_blueprint(errors_bp)

    # auth blueprint
    from app.auth import bp as auth_bp
    app.register_blueprint(auth_bp,  url_prefix='/auth')

    # core application 
    from app.main import bp as main_bp
    app.register_blueprint(main_bp)

    # cli blueprint
    from app.cli import bp as cli_bp
    app.register_blueprint(cli_bp)


    if not app.debug and not not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Microblog Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240,
                                        backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Microblog startup')
    
    return app

from app import models