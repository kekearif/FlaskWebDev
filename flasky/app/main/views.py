from flask import render_template
from . import main
# For the routing, use . to use from the __init__


@main.route('/')
def index():
    return render_template('index.html')
