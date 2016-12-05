import psycopg2
import requests
import json
from random import randint

try:
    conn = psycopg2.connect("dbname='rivercookie' user='filmdatify' host='fa16-cs411-06.cs.illinois.edu' password='veryInsecure74'")
except:
    print ("I am unable to connect to the database")
cur = conn.cursor()

file = open('location.txt', 'r')

data_file =  open('imdb250.json')    
MovieData = json.load(data_file)



for i in range(150):
	print ('Inserting User', i)
	if i % 2 == 0:
		resp = requests.get('https://randomuser.me/api/?gender=female').json()['results'][0]
		gender = 0
		interested_in = 1
	else:
		resp = requests.get('https://randomuser.me/api/?gender=male').json()['results'][0]
		gender = 1
		interested_in = 0

	filename = resp['picture']['large']
	name = resp['name']['first']+" "+resp['name']['last']
	password = '1234'
	email = 'fake0'+str(i)+'@gmail.com'
	birthdate = '1993-11-27'
	fake_location = file.readline().strip().split(',')
	provided_location = fake_location[0]
	location = 'POINT(%s %s)' % (fake_location[1],fake_location[2])

	sql = """INSERT INTO public.users (email, password, gender, interested_in, birthdate, name, location, picture_url, provided_location)
	VALUES (%(email)s, %(password)s, %(gender)s, %(interested_in)s, %(birthdate)s, %(name)s, ST_PointFromText(%(location)s, 4326), %(filename)s, %(provided_location)s)"""
	data = {'email': email, 'password': password, 'gender': gender, 'interested_in':interested_in, 'birthdate':birthdate ,'name':name, 'location':location, 'filename':filename, 'provided_location':provided_location}
	cur.execute(sql, data)
	cur.execute("SELECT id FROM public.users WHERE email = %(email)s", {'email': email})
	user_id = cur.fetchone()[0]
	for i in range(50):
		random_id = randint(0,249)
		title = MovieData[random_id]['title']
		cur.execute("SELECT id FROM public.movies WHERE title LIKE %(title)s", {'title': title})
		movie = cur.fetchone()
		if movie != None:
			sql = """INSERT INTO user_movie_opinions (user_id, movie_id, personal_rating, comments) VALUES (%(user_id)s, %(movie_id)s, %(personal_rating)s, 'Bot')"""
			data = {'user_id': user_id, 'movie_id':movie[0], 'personal_rating':randint(1,10)}
			cur.execute(sql, data)
	for i in range(50):
			person_id = randint(1,249)
			sql = """INSERT INTO user_person_opinions (user_id, person_id, personal_rating, comments) VALUES (%(user_id)s, %(person_id)s, %(personal_rating)s, 'Bot')"""
			data = {'user_id': user_id, 'person_id':str(person_id), 'personal_rating':randint(1,10)}
			cur.execute(sql, data)		
	conn.commit()



cur.close()
conn.close()
