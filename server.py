from app import app
from app.view import view
app.register_blueprint(view)

if __name__ == "__main__":
	app.run(host='localhost', port=5000)
