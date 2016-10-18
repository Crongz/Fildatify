from flask import Blueprint, render_template, abort
from jinja2 import TemplateNotFound

view = Blueprint('view', __name__, template_folder='templates', static_folder='static')

@view.route('/')
def home():
    try:
        return render_template('home.html')
    except TemplateNotFound:
        abort(404)
