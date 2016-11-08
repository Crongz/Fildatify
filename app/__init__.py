from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://filmdatify:veryInsecure74@fa16-cs411-06.cs.illinois.edu/filmdatify"
db = SQLAlchemy(app)

result = db.engine.execute("""SELECT * FROM "public"."users" """)
print (result)