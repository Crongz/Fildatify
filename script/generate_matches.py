import psycopg2

conn = psycopg2.connect("dbname='rivercookie' user='filmdatify' host='fa16-cs411-06.cs.illinois.edu' password='veryInsecure74'")
cur = conn.cursor()


cur.execute("SELECT user_a, user_b, match_factor, dist_miles FROM potential_matches_within_15_miles")
matches = cur.fetchall()

for match in matches:
    cur.execute("INSERT INTO matches (reason) VALUES(%s) RETURNING id", ("Match factor of %s - distance: %s miles" % (str(match[2]), str(match[3])),))
    new_id = cur.fetchone()[0]
    cur.execute("INSERT INTO matched_user (match_id, user_id) VALUES (%s, %s)", (new_id, match[0]))
    cur.execute("INSERT INTO matched_user (match_id, user_id) VALUES (%s, %s)", (new_id, match[1]))
    conn.commit()

    print("Generated match")

print("Done")
