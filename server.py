from app import app
from app.view import view
app.register_blueprint(view)

if __name__ == "__main__":
	app.run(host='fa16-cs411-06.cs.illinois.edu', port=5000)
