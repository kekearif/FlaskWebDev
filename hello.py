from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from datetime import datetime


app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)
# The __name__ argument is used for flask to determine the root path of the app
# Note how the ext is init the same as the others, passing the app in
# This moment object is now available in templates


@app.route('/')
def index():
    return render_template('index.html', current_time=datetime.utcnow())


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html')


if __name__ == '__main__':  # Only run dev server if script ex diretly
    app.run(debug=True)
