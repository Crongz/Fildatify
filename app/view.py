from flask import Blueprint, render_template, abort, flash, request, redirect, url_for
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename
from jinja2 import TemplateNotFound
from app import db, login_manager
from app.models import User
from app.forms import *
from sqlalchemy.sql import text
import os
import hashlib

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
    user = User()
    user.loadData(data)
    return user

"""
Home
"""
@view.route('/', methods=['GET'])
def home():
    return render_template('home.html')


"""
Dashboard
- User search movies, actors, directors and like them -> save like infomation into DB
- User see who they are match with 
- User can see suggested movies based on what they liked 
"""
@view.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    if request.method == 'POST':
        try:
            sql = "SELECT * FROM public.movies AS movies WHERE movies.title=:title OR movies.id IN (SELECT movie_people.movie_id FROM movie_people INNER JOIN people ON movie_people.movie_id=people.id AND people.name=:person)"
            result = connection.execute(text(sql), title=request.form['title'], person=request.form['person']).fetchall()
        except:
            flash('Failed to get movies', 'Error')
    return render_template('dashboard.html')

"""
Matches
"""
@view.route('/matches', methods=['GET'])
@login_required
def matches():
    if request.method == 'POST':
        try:
            sql = "INSERT INTO user_movie_opinions (user_id, movie_id, personal_rating, comment) VALUES (:user_id, :movie_id, :personal_rating, :comment)"
            connection.execute(text(sql), user_id=current_user.id, movie_id=movie_id, personal_rating= request.form['rating'], comment=request.form['comment'])
        except:
            flash('Failed to upload rating', 'Error')
    newMatch = None
    Matches = []
    try:
        sql = "SELECT user_id FROM matched_user WHERE user_id!=:current_id AND state=null AND match_id IN (SELECT match_id FROM matched_user WHERE user_id=:current_id AND state=null LIMIT 1)"
        newMatchID = connection.execute(text(sql), current_id=current_user.id).fetchone()
        if newMatchID != None:
            sql = "SELECT * FROM users WHERE id = :newMatchID)"
            newMatch = connection.execute(text(sql), newMatchID=newMatchID).fetchone()
    except:
        flash('Failed to get new match', 'Error')
    try:
        sql = "SELECT user_id FROM matched_user WHERE user_id!=:current_id AND state=true AND match_id IN (SELECT match_id FROM matched_user WHERE user_id=:current_id AND state=true LIMIT 1)"
        matchesID = connection.execute(text(sql), current_id=current_user.id).fetchall()
        for id in matchesID:
            sql = "SELECT * FROM users WHERE id = :matchID)"
            user = connection.execute(text(sql), matchID=id).fetchone()
            Matches.append(user)
    except:
        flash('Failed to get matches', 'Error')      
    return render_template('matches.html', newMatch=newMatch, Matches=Matches, matchesID=matchesID)

@view.route('/matchDetail', methods=['GET'])
@login_required
def matchDetail():
    return render_template('matchDetail.html')

@view.route('/movieDetail/<movie_id>', methods=['GET','POST'])
@login_required
def movieDetail(movie_id):
    if request.method == 'POST':
        try:
            sql = "INSERT INTO user_movie_opinions (user_id, movie_id, personal_rating, comment) VALUES (:user_id, :movie_id, :personal_rating, :comment)"
            connection.execute(text(sql), user_id=current_user.id, movie_id=movie_id, personal_rating= request.form['rating'], comment=request.form['comment'])
        except:
            flash('Failed to upload rating', 'Error')
    try:
        sql = "SELECT title, duration, year, plot, mpaa_rating FROM movies WHERE id=:id LIMIT 1"
        movie = connection.execute(text(sql), id=movie_id).fetchone()
    except:
        flash('Failed to get movie', 'Error')
    return render_template('movieDetail.html', movie=movie, movie_id=movie_id)


@view.route('/personDetail/<person_id>', methods=['GET', 'POST'])
@login_required
def personDetail(person_id):
    if request.method == 'POST':
        try:
            sql = "INSERT INTO user_person_opinions (user_id, movie_id, personal_rating, comment) VALUES (:user_id, :movie_id, :personal_rating, :comment)"
            connection.execute(text(sql), user_id=current_user.id, person_id=person_id, personal_rating= request.form['rating'], comment=request.form['comment'])
        except:
            flash('Failed to upload rating', 'Error')
    try:
        sql = "SELECT name, bio, birthdate, photo_url FROM people WHERE id=:id LIMIT 1"
        person = connection.execute(text(sql), id=person_id).fetchone()
    except:
        flash('Failed to find person', 'Error')
    return render_template('personDetail.html', person=person, person_id=person_id)

"""
Login
- Users can login with their email and password

Successful: Dashboard page (view.dashboard)
Failed: render Home page with Error

"""
@view.route('/login', methods=['POST'])
def login():
    sql = "SELECT * FROM public.users WHERE email=:email and password=:password LIMIT 1"
    result = connection.execute(text(sql), email=request.form['email'], password=request.form['password']).fetchone()
    if result != None:
        user = User()
        user.loadData(result)
        login_user(user)
        flash('Successfully Login', 'Success')
        return redirect(url_for('view.dashboard'))
    else:
        flash('Invalid password or email', 'Error')
    return redirect(url_for('view.home'))

"""
Logout
Successful: Home page (view.home)

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

Successful: Home page (view.home)
Failed: render Register page with Error
"""
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'])
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@view.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        try:
            file = request.files['file']
            filename = ''
            if file and allowed_file(file.filename):
                hashKey = hashlib.md5(file.read()).hexdigest() 
                filename = secure_filename(file.filename).rsplit('.', 1)[0]+ hashKey+ '.'+ secure_filename(file.filename).rsplit('.', 1)[1]
                file.save(os.path.join(APP_ROOT+'/UploadImage', filename))
            sql = "INSERT INTO public.users (email,password,gender,interested_in,birthdate,name,location,picture_url,provided_location) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}')"\
            .format(form.data['email'], form.data['password'], form.data['gender'], form.data['interested_in'], form.data['birthdate'], form.data['name'], form.data['location'],filename, form.data['zipcode'])
            connection.execute(sql)
            # sql = "SELECT * FROM public.users (email, password, gender, interested_in, birthdate, name, location) VALUES (:email, :password, :gender, :interested_in, :birthdate, :name, :location)"
            # connection.execute(text(sql), email=form.data['email'], password=form.data['password'], gender=form.data['gender'], interested_in=form.data['interested_in'], birthdate=form.data['birthdate'], name=form.data['name'], location=form.data['location'])
            flash('Successfully Registered', 'Success')
            return redirect(url_for('view.home'))
        except:
            flash('Something went wrong. Please try it again', 'Error')
    return render_template('register.html', form=form)

"""
Profile 
- Users can edit their profile 

Successful: New Profile page 
Failed: render Profile page with Error
"""
@view.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm(obj=current_user)
    if request.method == 'POST' and form.validate():
        try:
            file = request.files['file']
            filename = current_user.picture_url
            if file and allowed_file(file.filename):
                hashKey = hashlib.md5(file.read()).hexdigest() 
                filename = secure_filename(file.filename).rsplit('.', 1)[0]+ hashKey+ '.'+ secure_filename(file.filename).rsplit('.', 1)[1]
                file.save(os.path.join(APP_ROOT+'/UploadImage', filename))
            sql = "UPDATE public.users SET (gender,interested_in,birthdate,location,picture_url,provided_location) = ('{}','{}','{}','{}','{}','{}') WHERE ID = {}"\
            .format(form.data['gender'], form.data['interested_in'], form.data['birthdate'], form.data['location'], filename, form.data['provided_location'], current_user.id)
            connection.execute(sql)
            flash('Successfully Updated', 'Success')
            return redirect(url_for('view.profile'))
        except:
            flash('Something went wrong. Please try it again', 'Error')
    else:
        return render_template('profile.html', form=form)


@view.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')
