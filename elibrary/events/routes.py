from flask import render_template, url_for, request, flash, redirect, abort, Blueprint
from flask_login import login_required, current_user
from elibrary import db
from elibrary.models import Event
from elibrary.events.forms import FilterForm
from elibrary.utils.defines import PAGINATION
from sqlalchemy import desc

events = Blueprint('events', __name__)
sort_events_values = ['time', 'type', 'librarian', 'object_id']

@events.route("/events")
@login_required
def eventss():
    if not current_user.is_admin:
        abort(403)
    page = request.args.get('page', 1, type=int)
    sort_criteria = request.args.get('sort_by', 'time', type=str)
    sort_direction = request.args.get('direction', 'down', type=str)
    args_sort = {'sort_by': sort_criteria, 'direction': sort_direction}
    if not sort_criteria in sort_events_values:
        sort_criteria = 'time'

    filter_has_errors = False
    args_filter = {}
    form = FilterForm()
    my_query = db.session.query(Event)

    count_filtered = my_query.count()
    if filter_has_errors:
        flash(gettext('There are filter values with errors. However, valid filter values are applied.'), 'warning')
    if sort_direction == 'up':
        list = my_query.order_by(sort_criteria).paginate(page=page, per_page=PAGINATION)
    else:
        list = my_query.order_by(desc(sort_criteria)).paginate(page=page, per_page=PAGINATION)
    args_filter_and_sort = {**args_filter, **args_sort}
    return render_template('events.html', form=form, events_list=list, extra_filter_args=args_filter, extra_sort_and_filter_args=args_filter_and_sort, count_filtered=count_filtered)

@events.route("/events/details/<int:event_id>")
@login_required
def event_details(event_id):
    if not current_user.is_admin:
        abort(403)
    event = Event.query.get_or_404(event_id)
    return render_template('event.html', event=event)
