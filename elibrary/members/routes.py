from flask import render_template, url_for, redirect, request, flash, Blueprint, abort
from flask_login import current_user, login_required
from flask_babel import gettext, lazy_gettext as _l
from elibrary import db
# from elibrary.members.forms import ()
from elibrary.models import Member

members = Blueprint('members', __name__)

@members.route("/members")
@login_required
def members_all():
    return render_template('users.html', title='About')
