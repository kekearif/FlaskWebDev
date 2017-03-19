from flask import Flask, render_template
from flask.ext.bootstrap import Bootstrap
from flask.ext.moment import Moment
from datetime import datetime
from flask.ext.wtf import Form
from wtforms import StringField, SubmitField
from wtforms.validators import Required


app = Flask(__name__)
bootstrap = Bootstrap(app)
moment = Moment(app)
app.config['SECRET_KEY'] = 'sfd7868732hfayf92'
# The __name__ argument is used for flask to determine the root path of the app
# Note how the ext is init the same as the others, passing the app in
# This moment object is now available in templates
# The config is a dictionary. sec key is a config var used by flask and exts
# First wtf import is the flask ext
# The other two are from the wtforms package


class NameForm(Form):
    name = StringField('What is your name?', validators=[Required()])
    submit = SubmitField('Submit')


# GET is the default if we provide dict need to add get if need it
# Here we need a dict for the POST method on the form
@app.route('/', methods=['GET ', 'POST'])
def index():
    name = None
    form = NameForm()
    # Check all validators are ok
    if form.validate_on_submit:
        name = form.name.data  # When submit set the name
        form.name.data = ''    # Clear the field in the form
    return render_template('index.html', name=name, form=form)


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


@app.route('/shitform')
def shitform():
    form = NameForm()
    return render_template('shitform.html', form=form)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html')


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html')


if __name__ == '__main__':  # Only run dev server if script ex diretly
    app.run(debug=True)
