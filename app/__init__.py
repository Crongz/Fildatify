from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

app = Flask(__name__)

app.config.update(
    SQLALCHEMY_DATABASE_URI = "postgresql://filmdatify:veryInsecure74@fa16-cs411-06.cs.illinois.edu/rivercookie",
    SQLALCHEMY_TRACK_MODIFICATIONS = False,
    SECRET_KEY = 'veryInsecure74',
	DEBUG = True
)
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
