from flask import render_template, url_for, request, flash, redirect, abort, Blueprint
from flask_login import login_required, current_user
from flask_babel import gettext as _g
from elibrary import db
from elibrary.models import Event
from elibrary.events.forms import FilterForm
from elibrary.utils.common import CommonFilter
from elibrary.utils.custom_validations import string_cust, length_cust_max, numeric_cust, signature_cust, length_cust_max_15, FieldValidator
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
    args_page = {'page': page}
    if not sort_criteria in sort_events_values:
        sort_criteria = 'time'

    filter_has_errors = False
    args_filter = {}
    form = FilterForm()
    my_query = db.session.query(Event)
    f_date_from = request.args.get('date_from')
    f_date_to = request.args.get('date_to')
    f_librarian = request.args.get('librarian')
    f_object_id = request.args.get('object_id')
    f_type = request.args.get('type')
    f_is_seen = request.args.get('is_seen')

    my_query, args_filter, filter_has_errors = CommonFilter.process_related_date_filters(my_query,
        args_filter, filter_has_errors, form.date_from,
        form.date_to, f_date_from, f_date_to,
        'date_from', 'date_to', Event, 'time', False)

    my_query, args_filter, filter_has_errors = CommonFilter.process_like_filter(my_query, args_filter,
        filter_has_errors, form, form.librarian, f_librarian, 'librarian', [string_cust, length_cust_max], Event, 'librarian')

    my_query, args_filter, filter_has_errors = CommonFilter.process_equal_number_filter(my_query, args_filter,
        filter_has_errors, form.object_id, f_object_id, 'object_id', Event, 'object_id')

    if not (f_type == None or f_type == '0'):
        form.type.data = f_type
        my_query = my_query.filter(Event.type == f_type)
        args_filter['type'] = f_type

    if not (f_is_seen == None or f_is_seen == ""):
        form.is_seen.data = f_is_seen
        if f_is_seen == 'yes':
            my_query = my_query.filter(Event.is_seen == True)
            args_filter['is_seen'] = f_is_seen
        elif f_is_seen == 'no':
            my_query = my_query.filter(Event.is_seen == False)
            args_filter['is_seen'] = f_is_seen

    count_filtered = my_query.count()
    if filter_has_errors:
        flash(_g('There are filter values with errors. However, valid filter values are applied.'), 'warning')
    if sort_direction == 'up':
        list = my_query.order_by(sort_criteria).paginate(page=page, per_page=PAGINATION)
    else:
        list = my_query.order_by(desc(sort_criteria)).paginate(page=page, per_page=PAGINATION)
    args_filter_and_sort = {**args_filter, **args_sort}
    args_filter_sort_page = {**args_filter_and_sort, **args_page}
    return render_template('events.html', form=form, events_list=list, extra_filter_args=args_filter, extra_sort_and_filter_args=args_filter_and_sort, extra_sort_filter_page_args=args_filter_sort_page, count_filtered=count_filtered)

@events.route("/events/details/<int:event_id>")
@login_required
def event_details(event_id):
    if not current_user.is_admin:
        abort(403)
    event = Event.query.get_or_404(event_id)
    if not event.is_seen:
        event.is_seen = True
        db.session.commit()
    print(event.message)
    return render_template('event.html', event=event)

@events.route("/events/see/<int:event_id>")
@login_required
def event_seen(event_id):
    if not current_user.is_admin:
        abort(403)
    event = Event.query.get_or_404(event_id)
    event.is_seen = True
    db.session.commit()
    return redirect(url_for('events.eventss', **request.args))

@events.route("/events/unsee/<int:event_id>")
@login_required
def event_unseen(event_id):
    if not current_user.is_admin:
        abort(403)
    event = Event.query.get_or_404(event_id)
    event.is_seen = False
    db.session.commit()
    return redirect(url_for('events.eventss'))
