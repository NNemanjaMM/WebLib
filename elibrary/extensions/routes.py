from datetime import date#, timedelta
from sqlalchemy import desc, func, or_#, and_
from flask import render_template, url_for, Blueprint, request, flash, redirect#, abort
from flask_login import login_required,current_user
from flask_babel import gettext, lazy_gettext as _l
from elibrary import db
from elibrary.models import Extension, ExtensionPrice#, Member
from elibrary.utils.custom_validations import FieldValidator, string_cust, length_cust_max
from elibrary.extensions.forms import FilterForm, PriceUpdate, PriceAdd
from elibrary.utils.defines import PAGINATION#, EXPIRATION_EXTENSION_LIMIT, DATE_FORMAT, CURRENCY
#from elibrary.utils.common import Common
#from elibrary.main.forms import AcceptForm, RejectForm

extensions = Blueprint('extensions', __name__)

@extensions.route("/extensions")
@login_required
def extensionss():
    page = request.args.get('page', 1, type=int)
    sort_criteria = request.args.get('sort_by', 'id', type=str)
    sort_direction = request.args.get('direction', 'down', type=str)
    args_sort = {'sort_by': sort_criteria, 'direction': sort_direction}

    f_date_performed_from = request.args.get('date_performed_from')
    f_date_performed_to = request.args.get('date_performed_to')
    f_date_extended_from = request.args.get('date_extended_from')
    f_date_extended_to = request.args.get('date_extended_to')
    f_price = request.args.get('price')
    f_member_id = request.args.get('member_id')
    f_librarian_id = request.args.get('librarian_id')

    filter_has_errors = False
    args_filter = {}
    form = FilterForm()
    my_query = db.session.query(Extension)

    my_query, args_filter, filter_has_errors = process_related_date_filters(my_query,
            args_filter, filter_has_errors, form.date_performed_from,
            form.date_performed_to, f_date_performed_from, f_date_performed_to,
            'date_performed_from', 'date_performed_to', 'date_performed', True)

    my_query, args_filter, filter_has_errors = process_related_date_filters(my_query,
            args_filter, filter_has_errors, form.date_extended_from,
            form.date_extended_to, f_date_extended_from, f_date_extended_to,
            'date_extended_from', 'date_extended_to', 'date_extended', True)

    if not (f_price == None or f_price == ""):
        if not f_price == '__None':
            found = ExtensionPrice.query.filter_by(id=f_price).first()
            if found:
                form.price.data = found
                my_query = my_query.filter_by(price_id = f_price)
                args_filter['price'] = f_price
            else:
                filter_has_errors = True

    if not (f_member_id == None or f_member_id == ""):
        form.member_id.data = f_member_id
        from_value = FieldValidator.convert_and_validate_number(form.member_id)
        if not from_value == None:
            my_query = my_query.filter_by(member_id = from_value)
            args_filter['member_id'] = from_value
        else:
            filter_has_errors = True

    if not (f_librarian_id == None or f_librarian_id == ""):
        form.librarian_id.data = f_librarian_id
        from_value = FieldValidator.convert_and_validate_number(form.librarian_id)
        if not from_value == None:
            my_query = my_query.filter_by(librarian_id = from_value)
            args_filter['librarian_id'] = from_value
        else:
            filter_has_errors = True

    if filter_has_errors:
        flash(_l('There are filter values with errors')+'. '+_l('However, valid filter values are applied')+'.', 'warning')
    if sort_direction == 'up':
        list = my_query.order_by(sort_criteria).paginate(page=page, per_page=PAGINATION)
    else:
        list = my_query.order_by(desc(sort_criteria)).paginate(page=page, per_page=PAGINATION)
    args_filter_and_sort = {**args_filter, **args_sort}
    return render_template('extensions.html', form=form, extensions_list=list, extra_filter_args=args_filter, extra_sort_and_filter_args=args_filter_and_sort)

@extensions.route("/extensions/prices")
@login_required
def prices():
    if not current_user.is_admin:
        abort(403)
    sort_criteria = request.args.get('sort_by', 'id', type=str)
    sort_direction = request.args.get('direction', 'down', type=str)
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
        price.date_established = date.today()
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

def process_related_date_filters(my_query, args_filter, filter_has_errors, from_field, to_field, f_from, f_to, field_from_name, field_to_name, db_column_name, validate_future_date):
    from_value = None
    if not (f_from == None or f_from == ""):
        from_field.data = f_from
        from_value = FieldValidator.convert_and_validate_date(from_field, validate_future_date)
        if not from_value == None:
            my_query = my_query.filter(getattr(Extension, db_column_name) >= from_value.strftime('%Y-%m-%d'))
            args_filter[field_from_name] = f_from
        else:
            filter_has_errors = True
    if not (f_to == None or f_to == ""):
        to_field.data = f_to
        to_value = FieldValidator.convert_and_validate_date(to_field, validate_future_date)
        if not to_value == None:
            if not from_value == None:
                if FieldValidator.validate_date_order(from_value, to_value, to_field):
                    my_query = my_query.filter(getattr(Extension, db_column_name) <= to_value.strftime('%Y-%m-%d'))
                    args_filter[field_to_name] = f_to
                else:
                    filter_has_errors = True
            else:
                my_query = my_query.filter(getattr(Extension, db_column_name) <= to_value.strftime('%Y-%m-%d'))
                args_filter[field_to_name] = f_to
        else:
            filter_has_errors = True
    return my_query, args_filter, filter_has_errors
