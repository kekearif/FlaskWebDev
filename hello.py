from flask import Flask  # From the flask package import the class Flask
from flask import redirect  # The import is not from the venv folder flask
# Above we are importing the method redirect from flask
from flask import abort
from flask.ext.script import Manager
#  Import from the ext folder the module script and object Manager
app = Flask(__name__)
manager = Manager(app)  # Common to pass the app object to init ext things
# The __name__ argument is used for flask to determine the root path of the app


@app.route('/')
def index():  # This is the attached view function
    return "<h1>Hello world!</h1>"


@app.route('/user/<name>')
def user(name):
    return "<h1>Hello %s!" % name


@app.route('/error')
def error():
    return "Error status code 400 demo", 400  # Default is 200 code


@app.route('/google')
def google():
    return redirect('http://www.google.com')


@app.route('/mistake')
def mistake():
    abort(404)  # Hand back to server


if __name__ == '__main__':  # Only run dev server if script ex diretly
    #  app.run(debug=True)
    manager.run()  # Can use this for special command options now
