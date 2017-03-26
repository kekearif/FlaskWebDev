from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
# __init__.py tells python to treat dir as package
# We can also do other init work that is called when the package is used
# Above we import all objects we need
# Statements are called outside the app folder, can do import config ok

# Init with the app later
bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    # Above is a flask method to use config object
    # It will init the config itself
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)

    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    # Register our Blueprints

    return app
