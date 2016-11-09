from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)

app.config.update(
	# For prod
    SQLALCHEMY_DATABASE_URI = "postgresql://filmdatify:veryInsecure74@fa16-cs411-06.cs.illinois.edu/filmdatify",
    # For Localhost Dev
    # SQLALCHEMY_DATABASE_URI = "postgresql://filmdatify:veryInsecure74@localhost/filmdatify",
    SQLALCHEMY_TRACK_MODIFICATIONS = False,
    SECRET_KEY = 'veryInsecure74',
	DEBUG = True
)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)