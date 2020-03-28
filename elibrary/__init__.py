from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_babel import Babel
from elibrary.config import Config

db = SQLAlchemy()
bcrypt = Bcrypt()
babel = Babel()
login_manager = LoginManager()
login_manager.login_view = 'librarians.login'
login_manager.login_message_category = 'info'

@babel.localeselector
def get_locale():
    return 'sr'

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    babel.init_app(app)

    from elibrary.librarians.routes import librarians
    from elibrary.members.routes import members
    from elibrary.main.routes import main
    from elibrary.errors.handlers import errors
    app.register_blueprint(librarians)
    app.register_blueprint(members)
    app.register_blueprint(main)
    app.register_blueprint(errors)

    return app
