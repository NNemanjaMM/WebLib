from datetime import date, timedelta
from sqlalchemy import desc, or_, and_
from flask import render_template, url_for, redirect, request, flash, Blueprint
from flask_login import current_user, login_required
from flask_babel import gettext, lazy_gettext as _l
from elibrary import db
from elibrary.models import Member, Extension, Rental
from elibrary.utils.custom_validations import (string_cust, length_cust_max, FieldValidator)
from elibrary.members.forms import MemberCreateForm, MemberUpdateForm, FilterForm, ShortFilterForm
from elibrary.utils.defines import EXPIRATION_EXTENSION_LIMIT, PAGINATION, DATE_FORMAT, MAX_RENTED_BOOKS
from elibrary.utils.common import CommonFilter

members = Blueprint('members', __name__)
sort_member_values = ['id', 'first_name', 'last_name', 'total_books_rented', 'number_of_rented_books', 'date_registered', 'date_expiration']

@members.route("/members/details/<int:member_id>")
@login_required
def members_details(member_id):
    member = Member.query.get_or_404(member_id)
    extensions = Extension.query.filter_by(member_id=member_id).order_by(desc('date_performed'))
    rents = Rental.query.filter(and_(Rental.member_id==member_id, Rental.is_terminated==False)).order_by(desc('date_deadline'))
    return render_template('member.html', member=member, extensions=extensions, book_rentals=rents, max_books=MAX_RENTED_BOOKS)

@members.route("/members/create", methods=['GET', 'POST'])
@login_required
def members_create():
    form = MemberCreateForm()
    if form.validate_on_submit():
        member = Member()
        member.first_name = form.first_name.data
        member.last_name = form.last_name.data
        member.father_name = form.father_name.data
        member.profession = form.profession.data
        member.email = form.email.data
        member.phone = form.phone.data.replace("/", "")
        member.address = form.address.data
        member.date_registered = form.date_registered.data
        member.date_expiration = form.date_registered.data
        db.session.add(member)
        db.session.commit()
        flash(_l('New member has been added')+'.', 'success')
        return redirect(url_for('members.members_details', member_id=member.id))
    return render_template('member_cu.html', form=form, is_creating=True)

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
        form.phone.data = member.phone_print
        form.address.data = member.address
    return render_template('member_cu.html', form=form, is_creating=False)

@members.route("/members")
@login_required
def memberss(filtering = False, searching = False):
    page = request.args.get('page', 1, type=int)
    sort_criteria = request.args.get('sort_by', 'id', type=str)
    sort_direction = request.args.get('direction', 'up', type=str)
    args_sort = {'sort_by': sort_criteria, 'direction': sort_direction}
    if not sort_criteria in sort_member_values:
        sort_criteria = 'id'

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
        if FieldValidator.validate_field(form2, form2.text, [string_cust, length_cust_max]):
            my_query = my_query.filter(or_(Member.first_name.like('%' + s_text + '%'), Member.last_name.like('%' + s_text + '%'), Member.father_name.like('%' + s_text + '%'), Member.id == s_text))
            args_filter['text'] = s_text
    else:
        my_query, args_filter, filter_has_errors = CommonFilter.process_related_date_filters(my_query,
            args_filter, filter_has_errors, form.registration_date_from,
            form.registration_date_to, f_registration_date_from, f_registration_date_to,
            'registration_date_from', 'registration_date_to', Member, 'date_registered', False)

        my_query, args_filter, filter_has_errors = CommonFilter.process_related_date_filters(my_query,
            args_filter, filter_has_errors, form.expiration_date_from,
            form.expiration_date_to, f_expiration_date_from, f_expiration_date_to,
            'expiration_date_from', 'expiration_date_to', Member, 'date_expiration', False)

        my_query, args_filter, filter_has_errors = CommonFilter.process_related_number_filters(my_query,
            args_filter, filter_has_errors, form.books_rented_from,
            form.books_rented_to, f_books_rented_from, f_books_rented_to,
            'books_rented_from', 'books_rented_to', Member, 'total_books_rented')

        my_query, args_filter, filter_has_errors = CommonFilter.process_equal_number_filter(my_query, args_filter,
            filter_has_errors, form.id, f_id, 'id', Member, 'id')

        my_query, args_filter, filter_has_errors = CommonFilter.process_like_filter(my_query, args_filter, filter_has_errors,
            form, form.first_name, f_first_name, 'first_name', [string_cust, length_cust_max], Member, 'first_name')

        my_query, args_filter, filter_has_errors = CommonFilter.process_like_filter(my_query, args_filter, filter_has_errors,
            form, form.last_name, f_last_name, 'last_name', [string_cust, length_cust_max], Member, 'last_name')

        if not (f_has_rented_books == None or f_has_rented_books == ""):
            form.has_rented_books.data = f_has_rented_books
            if f_has_rented_books == 'yes':
                my_query = my_query.filter(Member.number_of_rented_books > 0)
                args_filter['has_rented_books'] = f_has_rented_books
            elif f_has_rented_books == 'no':
                my_query = my_query.filter(Member.number_of_rented_books == 0)
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

    count_filtered = my_query.count()
    if filter_has_errors:
        flash(_l('There are filter values with errors')+'. '+_l('However, valid filter values are applied')+'.', 'warning')
    if sort_direction == 'up':
        list = my_query.order_by(sort_criteria).paginate(page=page, per_page=PAGINATION)
    else:
        list = my_query.order_by(desc(sort_criteria)).paginate(page=page, per_page=PAGINATION)
    args_filter_and_sort = {**args_filter, **args_sort}
    return render_template('members.html', form=form, form2=form2, members_list=list, extra_filter_args=args_filter, extra_sort_and_filter_args=args_filter_and_sort, count_filtered = count_filtered)

@members.route("/membersr")
@login_required
def membersr():
    return memberss(False, True)

@members.route("/membersf")
@login_required
def membersf():
    return memberss(True, False)
