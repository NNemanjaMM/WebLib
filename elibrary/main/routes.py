from flask import render_template, url_for, redirect, request, flash, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flask_babel import gettext, lazy_gettext as _l
#from elibrary.main.forms import CreateBookForm, UpdateBookForm

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
@login_required
def home():
    return render_template('home.html')

@main.route("/members")
@login_required
def members():
    return render_template('users.html', title='About')

@main.route("/books")
@login_required
def books():
    return render_template('users.html', title='About')

@main.route("/stats")
@login_required
def stats():
    return render_template('users.html', title='About')
