from flask import render_template, url_for, redirect, request, flash, Blueprint
from flask_login import login_user, current_user, logout_user, login_required
from flask_babel import gettext as _g

main = Blueprint('main', __name__)

@main.route("/")
@main.route("/home")
@login_required
def home():
    return render_template('home.html')
