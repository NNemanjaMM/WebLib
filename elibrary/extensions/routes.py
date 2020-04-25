from datetime import date
from sqlalchemy import desc, func, or_
from flask import render_template, url_for, Blueprint, request, flash, redirect, abort
from flask_login import login_required,current_user
from flask_babel import gettext, lazy_gettext as _l
from elibrary import db
from elibrary.models import Extension, ExtensionPrice, Member
from elibrary.utils.custom_validations import FieldValidator, string_cust, length_cust_max
from elibrary.extensions.forms import FilterForm, ExtensionForm, PriceUpdate, PriceAdd
from elibrary.utils.defines import PAGINATION
from elibrary.utils.common import CommonFilter, CommonDate

extensions = Blueprint('extensions', __name__)
sort_extensions_values = ['date_performed', 'member_id', 'date_extended', 'price']
sort_prices_values = ['price_value', 'currency', 'is_enabled']

@extensions.route("/extensions")
@login_required
def extensionss():
    page = request.args.get('page', 1, type=int)
    sort_criteria = request.args.get('sort_by', 'id', type=str)
    sort_direction = request.args.get('direction', 'down', type=str)
    args_sort = {'sort_by': sort_criteria, 'direction': sort_direction}
    if not sort_criteria in sort_extensions_values:
        sort_criteria = 'id'

    f_date_performed_from = request.args.get('date_performed_from')
    f_date_performed_to = request.args.get('date_performed_to')
    f_date_extended_from = request.args.get('date_extended_from')
    f_date_extended_to = request.args.get('date_extended_to')
    f_price = request.args.get('price')
    f_member_id = request.args.get('member_id')

    filter_has_errors = False
    args_filter = {}
    form = FilterForm()
    my_query = db.session.query(Extension)

    my_query, args_filter, filter_has_errors = CommonFilter.process_related_date_filters(my_query,
            args_filter, filter_has_errors, form.date_performed_from,
            form.date_performed_to, f_date_performed_from, f_date_performed_to,
            'date_performed_from', 'date_performed_to', Extension, 'date_performed', False)

    my_query, args_filter, filter_has_errors = CommonFilter.process_related_date_filters(my_query,
            args_filter, filter_has_errors, form.date_extended_from,
            form.date_extended_to, f_date_extended_from, f_date_extended_to,
            'date_extended_from', 'date_extended_to', Extension, 'date_extended', False)

    if not (f_price == None or f_price == ""):
        if not f_price == '__None':
            found = ExtensionPrice.query.filter_by(id=f_price).first()
            if found:
                form.price.data = found
                my_query = my_query.filter_by(price_id = f_price)
                args_filter['price'] = f_price
            else:
                filter_has_errors = True

    my_query, args_filter, filter_has_errors = CommonFilter.process_equal_number_filter(my_query, args_filter,
        filter_has_errors, form.member_id, f_member_id, 'member_id', Extension, 'member_id')

    count_filtered = my_query.count()
    if filter_has_errors:
        flash(_l('There are filter values with errors')+'. '+_l('However, valid filter values are applied')+'.', 'warning')
    if sort_direction == 'up':
        list = my_query.order_by(sort_criteria).paginate(page=page, per_page=PAGINATION)
    else:
        list = my_query.order_by(desc(sort_criteria)).paginate(page=page, per_page=PAGINATION)
    args_filter_and_sort = {**args_filter, **args_sort}
    return render_template('extensions.html', form=form, extensions_list=list, extra_filter_args=args_filter, extra_sort_and_filter_args=args_filter_and_sort, count_filtered = count_filtered)

@extensions.route("/extensions/add/<int:member_id>", methods=['GET', 'POST'])
@login_required
def extensions_add(member_id):
    member = Member.query.get_or_404(member_id)
    if not (member.is_membership_near_expired or member.is_membership_expired):
        abort(405)
    form = ExtensionForm()
    form.date_expiration = member.date_expiration
    if form.validate_on_submit():
        if form.price.data.is_enabled:
            extension = Extension()
            extension.note = form.note.data
            extension.price = form.price.data.price_value
            extension.date_performed = form.date_performed.data
            extension.date_extended = CommonDate.add_year(extension.date_performed) if member.is_membership_expired else CommonDate.add_year(member.date_expiration)
            extension.member_id = member_id
            extension.price_id = form.price.data.id
            db.session.add(extension)
            member.date_expiration = extension.date_extended
            db.session.commit()
            flash(_l('Member\'s membership is successfuly extended to') + ' ' + member.date_expiration_print, 'info')
            return redirect(url_for('members.members_details', member_id=member.id))
    return render_template('extension_add.html', form=form, member=member)

@extensions.route("/extensions/prices")
@login_required
def prices():
    if not current_user.is_admin:
        abort(403)
    sort_criteria = request.args.get('sort_by', 'price_value', type=str)
    sort_direction = request.args.get('direction', 'down', type=str)
    if not sort_criteria in sort_prices_values:
        sort_criteria = 'price_value'

    my_query = db.session.query(ExtensionPrice)
    if sort_direction == 'up':
        list = my_query.order_by(sort_criteria).all()
    else:
        list = my_query.order_by(desc(sort_criteria)).all()
    return render_template('extension_prices.html', prices_list=list)

@extensions.route("/extensions/prices/add", methods=['GET', 'POST'])
@login_required
def prices_add():
    if not current_user.is_admin:
        abort(403)
    form = PriceAdd()
    if form.validate_on_submit():
        price = ExtensionPrice()
        price.price_value = form.price_value.data
        price.currency = form.currency.data
        price.note = form.note.data
        price.is_enabled = form.is_enabled.data
        db.session.add(price)
        db.session.commit()
        flash(_l('New price is added'), 'info')
        return redirect(url_for('extensions.prices'))
    return render_template('extension_prices_add.html', form=form)

@extensions.route("/extensions/prices/<int:price_id>", methods=['GET', 'POST'])
@login_required
def prices_update(price_id):
    if not current_user.is_admin:
        abort(403)
    price = ExtensionPrice.query.get_or_404(price_id)
    form = PriceUpdate()
    if form.validate_on_submit():
        price.note = form.note.data
        price.is_enabled = not price.is_enabled
        db.session.commit()
        flash(_l('Price availability is successfuly changed')+'.', 'success')
        return redirect(url_for('extensions.prices'))
    elif request.method == 'GET':
        form.note.data = price.note
    return render_template('extension_prices_update.html', form=form, price=price)
