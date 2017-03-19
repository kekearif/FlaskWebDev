from flask import Flask, render_template
app = Flask(__name__)
# The __name__ argument is used for flask to determine the root path of the app


@app.route('/')
def index():  # This is the attached view function
    return render_template('index.html')  # Looks in the templates folder


@app.route('/user/<name>')
def user(name):
    return render_template(
           'user.html', name=name, user=True, friends=["Bob", "Tim"])


if __name__ == '__main__':  # Only run dev server if script ex diretly
    app.run(debug=True)
