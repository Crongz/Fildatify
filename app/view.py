from flask import Blueprint, render_template, abort, flash, request, redirect, url_for
from flask_login import login_required, login_user, logout_user, current_user
from jinja2 import TemplateNotFound
from app import db, login_manager
from app.models import User
from app.forms import *
from sqlalchemy.sql import text


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
def dashboard():
    genre_options = [
        'Experimental',
        'Western',
        'Animation',
        'War',
        'History',
        'Musical',
        'Reality-TV',
        'Documentary',
        'Sci-Fi',
        'Short',
        'Thriller',
        'Film-Noir',
        'Biography',
        'Horror',
        'Action',
        'Comedy',
        'Commercial',
        'Family',
        'Adventure',
        'Talk-Show',
        'Lifestyle',
        'Romance',
        'Drama',
        'Fantasy',
        'Sport',
        'Mystery',
        'Crime',
        'Music'
    ]

    # ACTOR ROLE TYPE = (1,2) (actor,actress)
    # DIRECTOR=8

    # "WHERE title.kind_id=1 AND LOWER(name.name) LIKE \'%%%s%%\'"

    if request.method == 'POST':
        search_title = request.form['movie']
        search_genre = request.form['genrebox']
        search_actor = request.form["actor"]

        if search_title.strip() == "":
            search_title = None

        if search_actor.strip() == "":
            search_actor = None

        if search_genre.strip() == "":
            search_genre = None

        where = []
        params = {}

        if search_genre is not None:
            where.append("movie_info.info=:genre")
            params['genre'] = search_genre

        if search_actor is not None:
            where.append("LOWER(name.name) LIKE :actor_name")
            params['actor_name'] = '%' + search_actor.lower() + '%'

        if search_title is not None:
            where.append("LOWER(title.title) LIKE :movie_title")
            params['movie_title'] = '%' + search_title.lower() + '%'

        query = ''' SELECT DISTINCT ON (title.id) title.title, title.production_year FROM title
        LEFT JOIN cast_info ON cast_info.movie_id=title.id
        LEFT JOIN name ON cast_info.person_id=name.id
        LEFT JOIN movie_info ON movie_info.id=title.id
        WHERE 1=1
        '''

        if len(where) < 1:
            flash('Must provide at least one search term.', 'error')
            return render_template('dashboard.html', genre_options=sorted(genre_options))

        query += " AND "
        for i, clause in enumerate(where):
            query += clause + " "
            if i != len(where) - 1:
                query += " AND "

        query += " LIMIT 10"
        result = connection.execute(text(query), **params).fetchall()
        return render_template('dashboard.html', genre_options=sorted(genre_options),
                               last_title=search_title,
                               last_actor=search_actor,
                               last_genre=search_genre,
                               result=result
       )

    return render_template('dashboard.html', genre_options=sorted(genre_options))

"""
Match
"""
@view.route('/matchDetail', methods=['GET'])
def matchDetail():
    return render_template('matchDetail.html')

"""
Matches
"""
@view.route('/matches', methods=['GET'])
def matches():
    return render_template('matches.html')


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
        flash('Invalid passowrd or email', 'Error')
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
            sql = "INSERT INTO public.users (email,password,gender,interested_in,birthdate,name,location) VALUES ('{}','{}','{}','{}','{}','{}','{}')"\
            .format(form.data['email'], form.data['password'], form.data['gender'], form.data['interested_in'], form.data['birthdate'], form.data['name'], form.data['location'])
            connection.execute(sql)
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
            sql = "UPDATE public.users SET (gender,interested_in,birthdate,location) = ('{}','{}','{}','{}') WHERE ID = {}"\
            .format(form.data['gender'], form.data['interested_in'], form.data['birthdate'], form.data['location'], current_user.id)
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
