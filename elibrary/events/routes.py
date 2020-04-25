from flask import render_template, Blueprint
from flask_login import login_required, current_user

events = Blueprint('events', __name__)

@events.route("/events")
@login_required
def eventss():
    if not current_user.is_admin:
        abort(403)
    return render_template('events.html')
