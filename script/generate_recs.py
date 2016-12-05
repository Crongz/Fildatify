import psycopg2

conn = psycopg2.connect("dbname='rivercookie' user='filmdatify' host='fa16-cs411-06.cs.illinois.edu' password='veryInsecure74'")
cur = conn.cursor()

rec_query = '''
SELECT movie_id, (person_based_score + genre_based_score) / 2 AS rec_score
FROM (
       SELECT
         mid                         AS movie_id,
         AVG(person_based_rec_score) AS person_based_score,
         CASE WHEN AVG(user_genre_ratings.rating) IS NULL
           THEN 5
         ELSE
           AVG(user_genre_ratings.rating)
         END                         AS genre_based_score
       FROM
         (
           SELECT
             movie_people.movie_id AS mid,
             CASE WHEN SUM(computed_user_person_opinions.data_points) < 35
               THEN LEAST(
                   CAST(SUM(computed_user_person_opinions.data_points * computed_user_person_opinions.rating) AS FLOAT)
                   / CAST(SUM(computed_user_person_opinions.data_points) AS FLOAT), CAST(7 AS FLOAT)
               )
             ELSE
               CAST(SUM(computed_user_person_opinions.data_points * computed_user_person_opinions.rating) AS FLOAT)
               / CAST(SUM(computed_user_person_opinions.data_points) AS FLOAT)
             END                   AS person_based_rec_score


           FROM users
             INNER JOIN computed_user_person_opinions ON computed_user_person_opinions.uid = users.id
             INNER JOIN movie_people ON movie_people.person_id = computed_user_person_opinions.pid
          WHERE (
            SELECT COUNT(*) FROM user_movie_opinions WHERE user_movie_opinions.user_id=%(uid)d AND user_movie_opinions.movie_id=movie_people.movie_id
          ) = 0 AND
            (
            SELECT COUNT(*) FROM recommendations WHERE recommendations.user_id=%(uid)d AND recommendations.movie_id=movie_people.movie_id
          ) = 0

          AND users.id = %(uid)d
           GROUP BY movie_people.movie_id
           ORDER BY person_based_rec_score DESC
         ) person_query
         LEFT JOIN movie_genre ON movie_genre.movie_id = person_query.mid
         LEFT JOIN user_genre_ratings
           ON (user_genre_ratings.genre_id = movie_genre.genre_id AND user_genre_ratings.uid = %(uid)d)
       GROUP BY person_query.mid
 ) final
ORDER BY rec_score DESC
LIMIT 15
'''

cur.execute("SELECT id FROM users ORDER BY id")
ids = cur.fetchall()
ids = [i[0] for i in ids]

for i in ids:
    rec_query = rec_query % {'uid': i}
    cur.execute(rec_query)
    results = cur.fetchall()
    print("Generating recs for UID %d" % i)
    for result in results:
        q = 'INSERT INTO recommendations (user_id, movie_id) VALUES (%d, %d)' % (i, result[0])
        cur.execute(q)
        print("Added rec for UID %d" % i)


