from flask import Blueprint, render_template, abort, flash, request, redirect, url_for, jsonify
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.utils import secure_filename
from jinja2 import TemplateNotFound
from app import db, login_manager
from app.models import User
from app.forms import *
from sqlalchemy.sql import text
import os
import hashlib
import requests
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
    result = None
    if request.method == 'POST':
        try:
            title = request.form['title']
            person = request.form['person']
            if title == '' and person == '':
                return render_template('dashboard.html', result=result)
            elif title != '' and person == '':
                sql = "SELECT movies.id, title, duration, year, mpaa_rating FROM movies WHERE movies.title LIKE :title"
            elif title == '' and person != '':
                sql="SELECT movies.id, title, duration, year, mpaa_rating FROM movies INNER JOIN movie_people ON movies.id = movie_id INNER JOIN people ON person_id = people.id AND people.name LIKE :person"
            else:
                sql="SELECT movies.id, title, duration, year, mpaa_rating FROM movies INNER JOIN movie_people ON movies.id = movie_id INNER JOIN people ON person_id = people.id AND people.name LIKE :person WHERE movies.title LIKE :title"
            result = connection.execute(text(sql), title="%"+title+"%", person="%"+person+"%").fetchall()
        except:
            flash('Failed to get movies', 'Error')
    try:
        recommendations = []
        sql = "SELECT movies.id, title FROM movies INNER JOIN recommendations ON movies.id=recommendations.movie_id AND recommendations.user_id=:user_id LIMIT 10"
        recommendationsDB = connection.execute(text(sql), user_id=current_user.id).fetchall()
        for movie in recommendationsDB:
            response = requests.get('https://api.themoviedb.org/3/search/movie?api_key=f1e1b59caa89beb73c8529be3390ef01&language=en-US&query='+movie.title).json()
            if response['total_results'] != 0:
                TMDBid = response['results'][0]['id']
                movieExtra = requests.get('https://api.themoviedb.org/3/movie/'+str(TMDBid)+'?api_key=f1e1b59caa89beb73c8529be3390ef01&language=en-US').json()
                movieExtra['DBid'] = movie.id
                recommendations.append(movieExtra)
    except:
        flash('Failed to get recommendations', 'Error')
    return render_template('dashboard.html', result=result, recommendations=recommendations)

"""
Matches
"""
@view.route('/matches', methods=['GET'])
@login_required
def matches():
    if request.method == 'POST':
        try:
            sql = "INSERT INTO public.user_movie_opinions (user_id, movie_id, personal_rating, comment) VALUES (:user_id, :movie_id, :personal_rating, :comment)"
            connection.execute(text(sql), user_id=current_user.id, movie_id=movie_id, personal_rating= request.form['rating'], comment=request.form['comment'])
        except:
            flash('Failed to upload rating', 'Error')
    newMatch = None
    Matches = []
    # try:
    print('current_user.id',current_user.id)
    sql = "SELECT user_id FROM matched_user WHERE user_id!=:current_id AND state!=FALSE AND match_id IN (SELECT match_id FROM matched_user WHERE user_id=:current_id AND state=NULL) LIMIT 1"
    newMatchID = connection.execute(text(sql), current_id=current_user.id).fetchone()
    print('newMatchID',newMatchID)
    if newMatchID != None:
        sql = "SELECT * FROM users WHERE id = :newMatchID)"
        newMatch = connection.execute(text(sql), newMatchID=newMatchID).fetchone()
    # except:
    #     flash('Failed to get new match', 'Error')
    # try:
    #     sql = "SELECT user_id FROM matched_user WHERE user_id!=:current_id AND state=true AND match_id IN (SELECT match_id FROM matched_user WHERE user_id=:current_id AND state=true LIMIT 1)"
    #     matchesID = connection.execute(text(sql), current_id=current_user.id).fetchall()
    #     for id in matchesID:
    #         sql = "SELECT * FROM users WHERE id = :matchID)"
    #         user = connection.execute(text(sql), matchID=id).fetchone()
    #         Matches.append(user)
    # except:
    #     flash('Failed to get matches', 'Error')
    print('newMatch',newMatch)
    return render_template('matches.html', newMatch=newMatch, Matches=Matches, matchesID=matchesID)

@view.route('/matchDetail', methods=['GET'])
@login_required
def matchDetail():
    return render_template('matchDetail.html')

@view.route('/movieDetail/<movie_id>', methods=['GET','POST'])
@login_required
def movieDetail(movie_id):
    if request.method == 'POST':
        sql = "INSERT INTO public.user_movie_opinions (user_id, movie_id, personal_rating, comments) VALUES (:user_id, :movie_id, :personal_rating, :comments)"
        connection.execute(text(sql), user_id=str(current_user.id), movie_id=movie_id, personal_rating=str(2*int(request.form['rating'])), comments=request.form['comments'])
        return redirect(url_for('view.movieDetail', movie_id=movie_id))
    try:
        sql = '''
            SELECT title, duration, year, plot, mpaa_rating, 
            (SELECT string_agg(people.name, ', ') FROM movie_people LEFT JOIN people ON people.id=movie_people.person_id WHERE movie_people.person_role='Director' AND movie_people.movie_id=movies.id) 
            AS directors,
            (SELECT string_agg(people.name, '\n' ORDER BY people.name) FROM movie_people LEFT JOIN people ON people.id=movie_people.person_id WHERE movie_people.person_role='Actor' AND movie_people.movie_id=movies.id)  AS actors,
            string_agg(genre, ', ') AS genres FROM movies 
            LEFT JOIN movie_genre ON movie_genre.movie_id=movies.id 
            LEFT JOIN genres ON movie_genre.genre_id=genres.id

            WHERE movies.id=:id 
            GROUP BY movies.id, title, duration, year, plot, mpaa_rating
        '''
        movie = connection.execute(text(sql), id=movie_id).fetchone()
        sql ='''
            SELECT people.id, people.name
            FROM movie_people LEFT JOIN people ON people.id=movie_people.person_id 
            WHERE movie_people.person_role='Actor' AND movie_people.movie_id=:id
            ORDER BY people.name
        '''
        actors = connection.execute(text(sql), id=movie_id).fetchall()
        sql ='''
        SELECT COUNT(*)
        FROM user_movie_opinions
        WHERE user_id = :id AND movie_id = :movie_id
        '''
        exist = connection.execute(text(sql), id=current_user.id ,movie_id=movie_id).fetchone()
    except:
        flash('Failed to get movie', 'Error')
    response = requests.get('https://api.themoviedb.org/3/search/movie?api_key=f1e1b59caa89beb73c8529be3390ef01&language=en-US&query='+movie.title).json()
    if response['total_results'] != 0:
        TMDBid = response['results'][0]['id']
        movieExtra = requests.get('https://api.themoviedb.org/3/movie/'+str(TMDBid)+'?api_key=f1e1b59caa89beb73c8529be3390ef01&language=en-US').json()
    return render_template('movieDetail.html', movie=movie, movieExtra=movieExtra, movie_id=movie_id, actors=actors, count = exist.count)


@view.route('/personDetail/<person_id>', methods=['GET', 'POST'])
@login_required
def personDetail(person_id):
    if request.method == 'POST':
        try:
            sql = "INSERT INTO user_person_opinions (user_id, person_id, personal_rating, comments) VALUES (:user_id, :person_id, :personal_rating, :comments)"
            connection.execute(text(sql), user_id=current_user.id, person_id=person_id,personal_rating=str(2*int(request.form['rating'])), comments=request.form['comments'])
        except:
            flash('Failed to upload rating', 'Error')
        return redirect(url_for('view.personDetail', person_id=person_id))
    try:
        sql = "SELECT name, bio, birthdate, photo_url FROM people WHERE id=:id"
        person = connection.execute(text(sql), id=person_id).fetchone()
    except:
        flash('Failed to find person', 'Error')
    response = requests.get('https://api.themoviedb.org/3/search/person?api_key=f1e1b59caa89beb73c8529be3390ef01&language=en-US&query='+person.name).json()
    if response['total_results'] != 0:
        TMDBid = response['results'][0]['id']
        person = requests.get('https://api.themoviedb.org/3/person/'+str(TMDBid)+'?api_key=f1e1b59caa89beb73c8529be3390ef01&language=en-US').json()
        print (person)
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
@view.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        try:
            pair = form.data['location'].split(',')
            a = float(pair[0].strip('('))
            b = float(pair[1].strip(')'))

            location = 'POINT(%s %s)' % (str(b), str(a))
            sql = "INSERT INTO public.users " \
                  "(email, password, gender, interested_in, birthdate, name, location, picture_url, provided_location) " \
                  "VALUES (:email, :password, :gender, :interested_in, :birthdate, :name, ST_PointFromText(:location, 4326), :picture_url, :provided_location)"
            connection.execute(text(sql), email=form.data['email'], password=form.data['password'], gender=form.data['gender'], interested_in=form.data['interested_in'], birthdate=form.data['birthdate'], location=location, name=form.data['name'], picture_url=form.data['picture_url'], provided_location = form.data['provided_location'])
            flash('Successfully Registered', 'Success')
            return redirect(url_for('view.home'))
        except Exception as e:
            raise e
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
            pair = form.data['location'].split(',')
            a = float(pair[0].strip('('))
            b = float(pair[1].strip(')'))

            location = 'POINT(%s %s)' % (str(b), str(a))
            sql = "UPDATE public.users SET (gender,interested_in,birthdate,location,picture_url,provided_location) = ('{}','{}','{}','{}','{}','{}') WHERE ID = {}"\
            .format(form.data['gender'], form.data['interested_in'], form.data['birthdate'], location, form.data['picture_url'], form.data['provided_location'], current_user.id)
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
