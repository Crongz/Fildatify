from flask import Blueprint, render_template, abort, request, redirect, url_for
from flask_login import login_required, login_user, logout_user 
from jinja2 import TemplateNotFound
from app import db, login_manager
from app.models import User

view = Blueprint('view', __name__, template_folder='templates', static_folder='static')

connection = db.engine.connect()

"""
Exmaple of SQL
result = connection.execute('select * from public.users')
result: (9, 2, 2, datetime.date(2016, 10, 30), u'James Lee', '(40.7128,74.0059)', u'test@test.com', u'123')
"""

def Test_SQL():
    sql = "SELECT * FROM public.users WHERE email='test@test.com' and password='123' LIMIT 1"
    result = connection.execute(sql).fetchall()
    print result

@login_manager.user_loader
def load_user(user_id):
    sql = "SELECT * FROM public.users WHERE id='{}' LIMIT 1".format(user_id)
    result = connection.execute(sql).fetchone()
    return User(result)

"""
Dashboard
- User search movies, actors, directors and like them -> save like infomation into DB
- User see who they are match with 
- User can see suggested movies based on what they liked 
"""
@view.route('/', methods=['GET'])
def home():
    return render_template('home.html')

"""
Login
- Users can login with their email and password

Successful: Dashboard page (view.home)
Failed: render Login

"""
@view.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        sql = "SELECT * FROM public.users WHERE email='{}' and password='{}' LIMIT 1".format(request.form['email'], request.form['password'])
        result = connection.execute(sql).fetchone()
        print (result)
        if result != None:
            user = User(result)
            login_user(user)
        return redirect(url_for('view.home'))
    return render_template('login.html')

"""
Register
- Users can register with their information

Successful: Login page (view.login)
Failed: render Register page
"""
@view.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            sql = """INSERT INTO "public"."users" ("email","password","gender","interested_in","birthdate","name","location") VALUES ('%s','%s','%s', '%s', '%s', '%s', '%s')""" % (request.form['email'], request.form['password'], request.form['gender'], request.form['gender'], request.form['birthdate'], request.form['name'], '(40.7128, 74.0059)')
            cur.execute(sql)
        except:
            print ("Cannot Insert")

        return redirect(url_for('view.home'))
    else:
        return render_template('register.html')

"""
Profile 
- Users can edit their profile 

Successful: New Profile page 
Failed: render Profile page
"""
@view.route('/profile', methods=['GET','POST'])
def profile():
    return render_template('profile.html')


@view.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')
