from datetime import date, timedelta
from sqlalchemy import desc, or_, and_
from flask import render_template, url_for, redirect, request, flash, Blueprint, abort
from flask_login import current_user, login_required
from flask_babel import gettext, lazy_gettext as _l
from elibrary import db
from elibrary.models import Member
from elibrary.members.forms import (MemberCreateForm, MemberUpdateForm,
    UserExtensionForm, FilterForm, ShortFilterForm)
from elibrary.utils.numeric_defines import MEMBERSHIP_EXTENSION_DAYS, EXPIRATION_EXTENSION_LIMIT, PAGINATION
from elibrary.main.forms import AcceptForm, RejectForm
from elibrary.utils.custom_validations import (string_cust, length_cust_max, FieldValidator)

members = Blueprint('members', __name__)

@members.route("/members/details/<int:member_id>")
@login_required
def members_details(member_id):
    member = Member.query.get_or_404(member_id)
    return render_template('member.html', member=member)

@members.route("/members/create", methods=['GET', 'POST'])
@login_required
def members_create():
    form = MemberCreateForm()
    if form.validate_on_submit():
        member = Member()
        member.id = form.id.data
        member.first_name = form.first_name.data
        member.last_name = form.last_name.data
        member.father_name = form.father_name.data
        member.profession = form.profession.data
        member.email = form.email.data
        member.phone = form.phone.data.replace("/", "")
        member.address = form.address.data
        member.date_registered = form.date_registered.data
        member.date_expiration = form.date_registered.data + timedelta(MEMBERSHIP_EXTENSION_DAYS)
        db.session.add(member)
        db.session.commit()
        flash(_l('New member has been added')+'.', 'success')
        return redirect(url_for('members.memberss'))
    return render_template('member_create.html', form=form, is_creating=True)

@members.route("/members/update/<int:member_id>", methods=['GET', 'POST'])
@login_required
def members_update(member_id):
    member = Member.query.get_or_404(member_id)

    form = MemberUpdateForm()
    if form.validate_on_submit():
        member.first_name = form.first_name.data
        member.last_name = form.last_name.data
        member.father_name = form.father_name.data
        member.profession = form.profession.data
        member.email = form.email.data
        member.phone = form.phone.data.replace("/", "")
        member.address = form.address.data
        db.session.commit()
        flash(_l('Member data has been updated')+'.', 'success')
        return redirect(url_for('members.members_details',member_id=member.id))
    elif request.method == 'GET':
        form.first_name.data = member.first_name
        form.last_name.data = member.last_name
        form.father_name.data = member.father_name
        form.profession.data = member.profession
        form.email.data = member.email
        form.phone.data = member.phone_formated
        form.address.data = member.address
    return render_template('member_create.html', form=form, is_creating=False)

@members.route("/members/extend/<int:member_id>", methods=['GET', 'POST'])
@login_required
def members_extend(member_id):
    member = Member.query.get_or_404(member_id)
    if not member.is_membership_near_expired:
        abort(405)

    form = UserExtensionForm()
    if member.is_membership_expired:
        new_date_expiration = date.today() + timedelta(MEMBERSHIP_EXTENSION_DAYS)
    else:
        new_date_expiration = member.date_expiration + timedelta(MEMBERSHIP_EXTENSION_DAYS)
        form.fixed_value = True
    form.maximum_date = new_date_expiration

    if form.validate_on_submit():
        member.date_expiration = form.extension_date.data
        flash(_l('Member\'s membership is extended for')+' '+str(MEMBERSHIP_EXTENSION_DAYS)+' '+_l('days')+'.', 'info')
        db.session.commit()
        return redirect(url_for('members.members_details', member_id=member.id))

    form.extension_date.data = new_date_expiration
    return render_template('member_extension.html', form=form, member=member, expiration_proposal=new_date_expiration)

@members.route("/members")
@login_required
def memberss(filtering = False, searching = False):
    page = request.args.get('page', 1, type=int)
    sort_criteria = request.args.get('sort_by', 'id', type=str)
    sort_direction = request.args.get('direction', 'up', type=str)
    args_sort = {'sort_by': sort_criteria, 'direction': sort_direction}

    s_text = request.args.get('text')
    f_registration_date_from = request.args.get('registration_date_from')
    f_registration_date_to = request.args.get('registration_date_to')
    f_expiration_date_from = request.args.get('expiration_date_from')
    f_expiration_date_to = request.args.get('expiration_date_to')
    f_books_rented_from = request.args.get('books_rented_from')
    f_books_rented_to = request.args.get('books_rented_to')
    f_id = request.args.get('id')
    f_first_name = request.args.get('first_name')
    f_last_name = request.args.get('last_name')
    f_has_rented_books = request.args.get('has_rented_books')
    f_has_expired = request.args.get('has_expired')
    if filtering:
        s_text = None
    elif searching:
        f_registration_date_from = None
        f_registration_date_to = None
        f_expiration_date_from = None
        f_expiration_date_to = None
        f_books_rented_from = None
        f_books_rented_to = None
        f_id = None
        f_first_name = None
        f_last_name = None
        f_has_rented_books = None
        f_has_expired = None

    filter_has_errors = False
    args_filter = {}
    form = FilterForm()
    form2 = ShortFilterForm()
    my_query = db.session.query(Member)

    if not (s_text == None or s_text == ""):
        form2.text.data = s_text
        if FieldValidator.validate_field(form2, form2.text, [string_cust]):
            my_query = my_query.filter(or_(Member.first_name.like('%' + s_text + '%'), Member.last_name.like('%' + s_text + '%'), Member.id == s_text))
            args_filter['name'] = s_text
    else:
        my_query, args_filter, filter_has_errors = process_related_date_filters(my_query,
            args_filter, filter_has_errors, form.registration_date_from,
            form.registration_date_to, f_registration_date_from, f_registration_date_to,
            'registration_date_from', 'registration_date_to', 'date_registered', True)

        my_query, args_filter, filter_has_errors = process_related_date_filters(my_query,
            args_filter, filter_has_errors, form.expiration_date_from,
            form.expiration_date_to, f_expiration_date_from, f_expiration_date_to,
            'expiration_date_from', 'expiration_date_to', 'date_expiration', False)

        my_query, args_filter, filter_has_errors = process_related_number_filters(my_query,
            args_filter, filter_has_errors, form.books_rented_from,
            form.books_rented_to, f_books_rented_from, f_books_rented_to,
            'books_rented_from', 'books_rented_to', 'total_books_rented')

        if not (f_id == None or f_id == ""):
            form.id.data = f_id
            if FieldValidator.validate_field(form, form.id, [string_cust, length_cust_max]):
                my_query = my_query.filter(Member.id == f_id)
                args_filter['id'] = f_id
            else:
                filter_has_errors = True

        if not (f_first_name == None or f_first_name == ""):
            form.first_name.data = f_first_name
            if FieldValidator.validate_field(form, form.first_name, [string_cust, length_cust_max]):
                my_query = my_query.filter(Member.first_name.like('%' + f_first_name + '%'))
                args_filter['first_name'] = f_first_name
            else:
                filter_has_errors = True

        if not (f_last_name == None or f_last_name == ""):
            form.last_name.data = f_last_name
            if FieldValidator.validate_field(form, form.last_name, [string_cust, length_cust_max]):
                my_query = my_query.filter(Member.last_name.like('%' + f_last_name + '%'))
                args_filter['last_name'] = f_last_name
            else:
                filter_has_errors = True

        if not (f_has_rented_books == None or f_has_rented_books == ""):
            form.has_rented_books.data = f_has_rented_books
            if f_has_rented_books == 'has_rented':
    #TODO iskodirati kada se knjige povezu
                args_filter['has_rented_books'] = f_has_rented_books
            elif f_has_rented_books == 'does_not_have':
    #TODO iskodirati kada se knjige povezu
                args_filter['has_rented_books'] = f_has_rented_books

        if not (f_has_expired == None or f_has_expired == ""):
            form.has_expired.data = f_has_expired
            if f_has_expired == 'expired':
                my_query = my_query.filter(Member.date_expiration < date.today().strftime('%Y-%m-%d'))
                args_filter['has_expired'] = f_has_expired
            elif f_has_expired == 'near_expiration':
                compare_date = date.today() + timedelta(EXPIRATION_EXTENSION_LIMIT)
                my_query = my_query.filter(and_(Member.date_expiration <= compare_date.strftime('%Y-%m-%d'), Member.date_expiration >= date.today().strftime('%Y-%m-%d')))
                args_filter['has_expired'] = f_has_expired
            elif f_has_expired == 'active':
                my_query = my_query.filter(Member.date_expiration >= date.today().strftime('%Y-%m-%d'))
                args_filter['has_expired'] = f_has_expired

    if filter_has_errors:
        flash(_l('There are filter values with errors')+'. '+_l('However, valid filter values are applied')+'.', 'warning')
    if sort_direction == 'up':
        list = my_query.order_by(sort_criteria).paginate(page=page, per_page=PAGINATION)
    else:
        list = my_query.order_by(desc(sort_criteria)).paginate(page=page, per_page=PAGINATION)
    args_filter_and_sort = {**args_filter, **args_sort}
    return render_template('members.html', form=form, form2=form2, members_list=list, extra_filter_args=args_filter, extra_sort_and_filter_args=args_filter_and_sort)

@members.route("/membersr")
@login_required
def membersr():
    return memberss(False, True)

@members.route("/membersf")
@login_required
def membersf():
    return memberss(True, False)

def process_related_date_filters(my_query, args_filter, filter_has_errors, from_field, to_field, f_from, f_to, field_from_name, field_to_name, db_column_name, validate_future_date):
    from_value = None
    if not (f_from == None or f_from == ""):
        from_field.data = f_from
        from_value = FieldValidator.convert_and_validate_date(from_field, validate_future_date)
        if not from_value == None:
            my_query = my_query.filter(getattr(Member, db_column_name) >= from_value.strftime('%Y-%m-%d'))
            args_filter[field_from_name] = f_from
        else:
            filter_has_errors = True
    if not (f_to == None or f_to == ""):
        to_field.data = f_to
        to_value = FieldValidator.convert_and_validate_date(to_field, validate_future_date)
        if not to_value == None:
            if not from_value == None:
                if FieldValidator.validate_date_order(from_value, to_value, to_field):
                    my_query = my_query.filter(getattr(Member, db_column_name) <= to_value.strftime('%Y-%m-%d'))
                    args_filter[field_to_name] = f_to
                else:
                    filter_has_errors = True
            else:
                my_query = my_query.filter(getattr(Member, db_column_name) <= to_value.strftime('%Y-%m-%d'))
                args_filter[field_to_name] = f_to
        else:
            filter_has_errors = True
    return my_query, args_filter, filter_has_errors

def process_related_number_filters(my_query, args_filter, filter_has_errors, from_field, to_field, f_from, f_to, field_from_name, field_to_name, db_column_name):
    from_value = None
    if not (f_from == None or f_from == ""):
        from_field.data = f_from
        from_value = FieldValidator.convert_and_validate_number(from_field)
        if not from_value == None:
            my_query = my_query.filter(getattr(Member, db_column_name) >= from_value)
            args_filter[field_from_name] = f_from
        else:
            filter_has_errors = True
    if not (f_to == None or f_to == ""):
        to_field.data = f_to
        to_value = FieldValidator.convert_and_validate_number(to_field)
        if not to_value == None:
            if not from_value == None:
                if FieldValidator.validate_number_order(from_value, to_value, to_field):
                    my_query = my_query.filter(getattr(Member, db_column_name) <= to_value)
                    args_filter[field_to_name] = f_to
                else:
                    filter_has_errors = True
            else:
                my_query = my_query.filter(getattr(Member, db_column_name) <= to_value)
                args_filter[field_to_name] = f_to
        else:
            filter_has_errors = True
    return my_query, args_filter, filter_has_errors
