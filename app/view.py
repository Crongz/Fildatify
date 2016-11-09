from flask import Blueprint, render_template, abort, flash, request, redirect, url_for
from flask_login import login_required, login_user, logout_user 
from jinja2 import TemplateNotFound
from sqlalchemy.sql import text, bindparam
from app import db, login_manager
from app.models import User

view = Blueprint('view', __name__, template_folder='templates', static_folder='static')

connection = db.engine.connect()

"""
Exmaple of SQL:
Format connection.execute('WHATEVRE SQL QUERY') .fetchone() return tuple and fetchall() return list of tuples
If you know SQL Query is going to return only ONE tuple because you used something like 'LIMIT 1' then use .fetchone()
Otherwise use .fetchall()

There is exmaple below:
"""

'''
result = connection.execute('select * from public.users WHERE id='9' LIMIT 1).fetchone()
print result -> (9, 2, 2, datetime.date(2016, 10, 30), u'James Lee', '(40.7128,74.0059)', u'test@test.com', u'123')

result = connection.execute('select * from public.users).fetchall()
print result -> 
[(7, 2, 2, datetime.date(2012, 11, 29), u'James Lee', '(40.7128,74.0059)', u'leejamesws@gmail.com', u'123'), 
 (9, 2, 2, datetime.date(2016, 10, 30), u'James Lee', '(40.7128,74.0059)', u'test@test.com', u'123'), 
 (11, 1, 0, datetime.date(1996, 8, 18), u'Vanessa Wang', '(123,123)', u'viwang2@illinois.edu', u'123')]
'''


@login_manager.user_loader
def load_user(user_id):
    sql = "SELECT * FROM public.users WHERE id='{}' LIMIT 1".format(user_id)
    data = connection.execute(sql).fetchone()
    return User(data)

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
Failed: render Home page

"""
@view.route('/login', methods=['POST'])
def login():
    sql = "SELECT * FROM public.users WHERE email='{}' and password='{}' LIMIT 1".format(request.form['email'], request.form['password'])
    result = connection.execute(sql).fetchone()
    if result != None:
        user = User(result)
        login_user(user)
        flash('Successfully Login', 'Success')
    else:
        flash('Invalid passowrd or email', 'Error')
    return redirect(url_for('view.home'))

"""
Logout
"""
@view.route("/logout")
@login_required
def logout():
    logout_user()
    flash('Successfully Logout', 'Success')
    return redirect(url_for('view.home'))

"""
Register
- Users can register with their information

Successful: Login page (view.login)
Failed: render Home page
"""
@view.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        try:
            sql = "INSERT INTO public.users (email,password,gender,interested_in,birthdate,name,location) VALUES ('{}','{}','{}','{}','{}','{}','{}')"\
            .format(request.form['email'], request.form['password'], request.form['gender'], request.form['gender'], request.form['birthdate'], request.form['name'], '(40.7128, 74.0059)')
            connection.execute(sql)
            flash('Successfully Login', 'Success')
            return redirect(url_for('view.home'))
        except:
            flash('Something went wrong. Please try it again', 'Error')
            return render_template('register.html')
    else:
        return render_template('register.html')

"""
Profile 
- Users can edit their profile 

Successful: New Profile page 
Failed: render Profile page
"""
@view.route('/profile', methods=['GET','POST'])
@login_required
def profile():
    if request.method == 'POST':
        return render_template('profile.html')
    else:
        return render_template('profile.html')


@view.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')
