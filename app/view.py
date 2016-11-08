from flask import Blueprint, render_template, abort, request, redirect, url_for
from jinja2 import TemplateNotFound
from app.models import User
import psycopg2

view = Blueprint('view', __name__, template_folder='templates', static_folder='static')


try:
    conn = psycopg2.connect(dbname='filmdatify', user='filmdatify', host='fa16-cs411-06.cs.illinois.edu', port=5432 , password='veryInsecure74')
    conn.autocommit = True
    cur = conn.cursor()
except:
    print ("I am unable to connect to the database")

@view.route('/', methods=['GET'])
def home():
    try:
        user_sql = """SELECT * FROM "public"."users" """
        cur.execute(user_sql)
        user_query = cur.fetchall()
    except:
        user_query = ['No space, VM has too little space for us :(']

    try:
        title_sql = """SELECT * FROM "public"."cast_info" WHERE movie_id = 287640 LIMIT 50"""
        cur.execute(title_sql)
        title_query=cur.fetchmany(20)
    except:
        title_query = ['No space, VM has too little space for us :(']

    try:
        join_sql = """SELECT title.title, name.name FROM title
                    INNER JOIN cast_info ON cast_info.movie_id = title.id
                    INNER JOIN name      ON name.id = cast_info.person_id
                    WHERE title like '%Batman%'
                    LIMIT 50 """
        cur.execute(join_sql)
        join_query=cur.fetchmany(20)
    except:
        join_query = ['No space, VM has too little space for us :(']

    return render_template('home.html', users=user_query, movies=title_query, joins=join_query)

@view.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        try:
            login_sql = """SELECT * FROM "public"."users" WHERE email='%s' and password='%s' """ % (request.form['email'], request.form['password'])
            cur.execute(login_sql)
            data = cur.fetchone()
            return render_template('login.html', data=data)
        except:
            print ("Cannot Select")
            return render_template('login.html')
    return render_template('login.html')

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

@view.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')
