from datetime import date, timedelta
from flask import render_template, url_for, request, flash, redirect, abort, Blueprint
from flask_login import login_required, current_user
from flask_babel import gettext, lazy_gettext as _l
from elibrary import db
from elibrary.models import Book, Member, Rental
from elibrary.utils.common import CommonFilter
from elibrary.utils.defines import PAGINATION, MAX_RENTED_BOOKS, RENTAL_DATE_LIMIT, DATE_FORMAT, BOOK_RENT_PERIOD
from elibrary.utils.custom_validations import string_cust, length_cust_max, numeric_cust, signature_cust, length_cust_max_15, FieldValidator
from elibrary.books.forms import FilterForm, SearchForm, BookCreateUpdateForm, RentForm, RentTerminationForm, RentFilterForm
from sqlalchemy import desc, or_, and_, func, text
from sqlalchemy.sql.operators import is_

books = Blueprint('books', __name__)
sort_prices_values = ['inv_number', 'signature', 'title', 'author']
sort_rents_values = ['date_performed', 'date_deadline', 'date_termination', 'is_terminated']

@books.route("/books")
@login_required
def bookss(filtering = False, searching = False):
    page = request.args.get('page', 1, type=int)
    sort_criteria = request.args.get('sort_by', 'inv_number', type=str)
    sort_direction = request.args.get('direction', 'up', type=str)
    args_sort = {'sort_by': sort_criteria, 'direction': sort_direction}
    if not sort_criteria in sort_prices_values:
        sort_criteria = 'inv_number'

    s_text = request.args.get('text')
    f_inv_number = request.args.get('inv_number')
    f_signature = request.args.get('signature')
    f_title = request.args.get('title')
    f_author = request.args.get('author')
    f_is_rented = request.args.get('is_rented')
    f_has_error = request.args.get('has_error')
    if filtering:
        s_text = None
    elif searching:
        f_inv_number = None
        f_signature = None
        f_title = None
        f_author = None
        f_is_rented = None
        f_has_error = None

    filter_has_errors = False
    args_filter = {}
    form = FilterForm()
    form2 = SearchForm()
    my_query = db.session.query(Book)

    if not (s_text == None or s_text == ""):
        form2.text.data = s_text
        if FieldValidator.validate_field(form2, form2.text, [string_cust, length_cust_max]):
            my_query = my_query.filter(or_(Book.inv_number == s_text, Book.signature.like('%' + s_text + '%'),
                Book.title.like('%' + s_text + '%'), Book.author.like('%' + s_text + '%')))
            args_filter['text'] = s_text
    else:
        my_query, args_filter, filter_has_errors = CommonFilter.process_like_filter(my_query, args_filter,
            filter_has_errors, form, form.inv_number, f_inv_number, 'inv_number', [numeric_cust, length_cust_max], Book, 'inv_number')

        my_query, args_filter, filter_has_errors = CommonFilter.process_like_filter(my_query, args_filter,
            filter_has_errors, form, form.signature, f_signature, 'signature', [string_cust, length_cust_max], Book, 'signature')

        my_query, args_filter, filter_has_errors = CommonFilter.process_like_filter(my_query, args_filter,
            filter_has_errors, form, form.title, f_title, 'title', [string_cust, length_cust_max], Book, 'title')

        my_query, args_filter, filter_has_errors = CommonFilter.process_like_filter(my_query, args_filter,
            filter_has_errors, form, form.author, f_author, 'author', [string_cust, length_cust_max], Book, 'author')

        if not (f_is_rented == None or f_is_rented == ""):
            form.is_rented.data = f_is_rented
            if f_is_rented == 'yes':
                my_query = my_query.filter(Book.is_rented == True)
                args_filter['is_rented'] = f_is_rented
            elif f_is_rented == 'no':
                my_query = my_query.filter(Book.is_rented == False)
                args_filter['is_rented'] = f_is_rented

        if not (f_has_error == None or f_has_error == ""):
            form.has_error.data = f_has_error
            if f_has_error == 'yes':
                my_query = my_query.filter(Book.has_error == True)
                args_filter['has_error'] = f_has_error
            elif f_has_error == 'no':
                my_query = my_query.filter(Book.has_error == False)
                args_filter['has_error'] = f_has_error

    count_filtered = my_query.count()
    if filter_has_errors:
        flash(_l('There are filter values with errors')+'. '+_l('However, valid filter values are applied')+'.', 'warning')
    if sort_direction == 'up':
        list = my_query.order_by(sort_criteria).paginate(page=page, per_page=PAGINATION)
    else:
        list = my_query.order_by(desc(sort_criteria)).paginate(page=page, per_page=PAGINATION)
    args_filter_and_sort = {**args_filter, **args_sort}
    return render_template('books.html', form=form, form2=form2, books_list=list, extra_filter_args=args_filter, extra_sort_and_filter_args=args_filter_and_sort, count_filtered = count_filtered)

@books.route("/booksr")
@login_required
def booksr():
    return bookss(False, True)

@books.route("/booksf")
@login_required
def booksf():
    return bookss(True, False)

@books.route("/books/update/<int:book_id>", methods=['GET', 'POST'])
@login_required
def books_update(book_id):
    form = BookCreateUpdateForm()
    book = Book.query.get_or_404(book_id)
    if form.validate_on_submit():
        book.inv_number = form.inv_number.data
        book.signature = form.signature.data
        book.title = form.title.data
        book.author = form.author.data
        if current_user.is_admin:
            book.has_error = form.has_error.data
        db.session.commit()
        flash(_l('Book is successfuly updated')+'.', 'success')
        return redirect(url_for('books.bookss'))
    elif request.method == 'GET':
        form.inv_number.data = book.inv_number
        form.signature.data = book.signature
        form.title.data = book.title
        form.author.data = book.author
        form.has_error.data = book.has_error
    return render_template('books_cu.html', form=form, is_creating=False)

@books.route("/books/add", methods=['GET', 'POST'])
@login_required
def books_add():
    form = BookCreateUpdateForm()
    if form.validate_on_submit():
        book = Book()
        book_duplicate = Book.query.filter(Book.inv_number==form.inv_number.data).first()
        book.inv_number = form.inv_number.data
        book.signature = form.signature.data
        book.title = form.title.data
        book.author = form.author.data
        if book_duplicate:
            book_duplicate.has_error = True
            book.has_error = True
            flash(_l('Book with the same inventory number already exists')+'!', 'warning')
        db.session.add(book)
        db.session.commit()
        flash(_l('Book is successfuly added')+'.', 'success')
        return redirect(url_for('books.bookss'))
    return render_template('books_cu.html', form=form, is_creating=True)

@books.route("/books/rent/<int:member_id>", methods=['GET', 'POST'])
@login_required
def book_rent(member_id):
    member = Member.query.get_or_404(member_id)
    if member.is_membership_expired or member.number_of_rented_books >= MAX_RENTED_BOOKS:
        abort(405)
    message = None
    form = RentForm()
    if form.search.data and form.validate():
        book_inv = to_value = FieldValidator.convert_and_validate_number(form.inv_number)
        if book_inv:
            book = Book.query.filter(Book.inv_number == book_inv).first()
            form.inv_number.data = book_inv
            if book:
                form.signature.data = book.signature
                form.title.data = book.title
                form.author.data = book.author
                if book.is_rented:
                    message = _l('Book with this inventory number is already rented') + '. ' +_l('Please check your inventory number and then continue') + '.'
            else:
                form.signature.data = None
                form.title.data = None
                form.author.data = None
                message = _l('Book with this inventory number was not found')
    elif form.submit.data and form.validate():
        failed_1 = not FieldValidator.convert_and_validate_number(form.inv_number)
        failed_2 = not FieldValidator.validate_required_field(form, form.signature, [signature_cust, length_cust_max_15])
        failed_3 = not FieldValidator.validate_required_field(form, form.title, [string_cust, length_cust_max])
        failed_4 = not FieldValidator.validate_required_field(form, form.author, [string_cust, length_cust_max])
        date_value = FieldValidator.convert_and_validate_date(form.date_rented, False, (date.today()-timedelta(RENTAL_DATE_LIMIT)).strftime(DATE_FORMAT))
        if not (failed_1 or failed_2 or failed_3 or failed_4 or date_value == None):
            book_id = None
            book_duplicate = Book.query.filter(Book.inv_number==form.inv_number.data).first()
            if book_duplicate and not book_duplicate.is_rented:
                book_id = book_duplicate.id
                book_duplicate.is_rented = True
                flash(_l('Book with the same inventory number already exists')+'.', 'info')
            else:
                new_book = Book()
                new_book.inv_number = form.inv_number.data
                new_book.signature = form.signature.data
                new_book.title = form.title.data
                new_book.author = form.author.data
                new_book.is_rented = True
                if book_duplicate and book_duplicate.is_rented:
                    book_duplicate.has_error = True
                    new_book.has_error = True
                    flash(_l('Book with the same inventory number is already rented')+'! '+_l('An error flag is set to the books with same inventory number')+'.', 'warning')
                db.session.add(new_book)
                db.session.commit()
                book_id = new_book.id
                flash(_l('New book is successfuly added')+'.', 'info')
            rental = Rental()
            rental.date_performed = date_value
            rental.date_deadline = date_value + timedelta(BOOK_RENT_PERIOD)
            rental.book_id = book_id
            rental.member_id = member_id
            db.session.add(rental)
            member.number_of_rented_books = db.session.query(func.count(Rental.id)).filter(and_(Rental.member_id == member_id, Rental.is_terminated == False)).scalar()
            member.total_books_rented = db.session.query(func.count(Rental.id)).filter(Rental.member_id == member_id).scalar()
            db.session.commit()
            flash(_l('Book is successfuly rented')+'.', 'info')
            return redirect(url_for('members.members_details', member_id=member_id))
    return render_template('renting.html', form=form, message=message)

@books.route("/books/rents/<int:rent_id>", methods=['GET', 'POST'])
@login_required
def book_rents_details(rent_id):
    rent = Rental.query.get_or_404(rent_id)
    member = Member.query.get_or_404(rent.member_id)
    book = Book.query.get_or_404(rent.book_id)
    form = RentTerminationForm()
    form.date_rented = rent.date_performed
    if not rent.is_terminated and form.validate_on_submit():
        rent.is_terminated = True
        rent.date_termination = form.date_returned.data
        member.number_of_rented_books = db.session.query(func.count(Rental.id)).filter(and_(Rental.member_id == member.id, Rental.is_terminated == False)).scalar()
        book.is_rented = False
        db.session.commit()
        flash(_l('Book is successfuly returned')+'.', 'info')
        return redirect(url_for('members.members_details', member_id=member.id))
    return render_template('rent.html', form=form, rent=rent)

@books.route("/books/rents/find/<int:book_id>")
@login_required
def book_rents_find(book_id):
    rent = Rental.query.filter(and_(Rental.book_id==book_id, Rental.is_terminated==False)).first()
    rent_id = rent.id if not rent == None else 1010101
    return redirect(url_for('books.book_rents_details', rent_id=rent_id))

@books.route("/books/rents")
@login_required
def book_rents():
    page = request.args.get('page', 1, type=int)
    sort_criteria = request.args.get('sort_by', 'id', type=str)
    sort_direction = request.args.get('direction', 'down', type=str)
    args_sort = {'sort_by': sort_criteria, 'direction': sort_direction}
    if not sort_criteria in sort_rents_values:
        sort_criteria = 'date_performed'

    filter_has_errors = False
    args_filter = {}
    form = RentFilterForm()
    my_query = db.session.query(Rental)

    f_date_performed_from = request.args.get('date_performed_from')
    f_date_performed_to = request.args.get('date_performed_to')
    f_date_deadline_from = request.args.get('date_deadline_from')
    f_date_deadline_to = request.args.get('date_deadline_to')
    f_date_terminated_from = request.args.get('date_terminated_from')
    f_date_terminated_to = request.args.get('date_terminated_to')
    f_is_terminated = request.args.get('is_terminated')
    f_is_deadlime_passed = request.args.get('is_deadlime_passed')
    f_book_id = request.args.get('book_id')
    f_member_id = request.args.get('member_id')

    my_query, args_filter, filter_has_errors = CommonFilter.process_related_date_filters(my_query,
        args_filter, filter_has_errors, form.date_performed_from,
        form.date_performed_to, f_date_performed_from, f_date_performed_to,
        'date_performed_from', 'date_performed_to', Rental, 'date_performed', False)

    my_query, args_filter, filter_has_errors = CommonFilter.process_related_date_filters(my_query,
        args_filter, filter_has_errors, form.date_deadline_from,
        form.date_deadline_to, f_date_deadline_from, f_date_deadline_to,
        'date_deadline_from', 'date_deadline_to', Rental, 'date_deadline', False)

    my_query, args_filter, filter_has_errors = CommonFilter.process_related_date_filters(my_query,
        args_filter, filter_has_errors, form.date_terminated_from,
        form.date_terminated_to, f_date_terminated_from, f_date_terminated_to,
        'date_terminated_from', 'date_terminated_to', Rental, 'date_termination', False)

    my_query, args_filter, filter_has_errors = CommonFilter.process_equal_number_filter(my_query, args_filter,
        filter_has_errors, form.book_id, f_book_id, 'book_id', Rental, 'book_id')

    my_query, args_filter, filter_has_errors = CommonFilter.process_equal_number_filter(my_query, args_filter,
        filter_has_errors, form.member_id, f_member_id, 'member_id', Rental, 'member_id')

    if not (f_is_terminated == None or f_is_terminated == ""):
        form.is_terminated.data = f_is_terminated
        if f_is_terminated == 'yes':
            my_query = my_query.filter(Rental.is_terminated == True)
            args_filter['is_terminated'] = f_is_terminated
        elif f_is_terminated == 'no':
            my_query = my_query.filter(Rental.is_terminated == False)
            args_filter['is_terminated'] = f_is_terminated

    can_sort = True
    if not (f_is_deadlime_passed == None or f_is_deadlime_passed == ""):
        form.is_deadlime_passed.data = f_is_deadlime_passed
        can_sort = False
        if f_is_deadlime_passed == 'yes':
            my_query1 = my_query.filter(and_(date.today() > Rental.date_deadline, Rental.is_terminated == False))
            my_query2 = my_query.filter(and_(Rental.date_termination > Rental.date_deadline, Rental.is_terminated == True))
            my_query = my_query1.union(my_query2)
            args_filter['is_deadlime_passed'] = f_is_deadlime_passed
        elif f_is_deadlime_passed == 'no':
            my_query1 = my_query.filter(and_(date.today() <= Rental.date_deadline, Rental.is_terminated == False))
            my_query2 = my_query.filter(and_(Rental.date_termination <= Rental.date_deadline, Rental.is_terminated == True))
            my_query = my_query1.union(my_query2)
            args_filter['is_deadlime_passed'] = f_is_deadlime_passed

    count_filtered = my_query.count()
    if filter_has_errors:
        flash(_l('There are filter values with errors')+'. '+_l('However, valid filter values are applied')+'.', 'warning')
    if not can_sort:
        list = my_query.paginate(page=page, per_page=PAGINATION)
    elif sort_direction == 'up':
        list = my_query.order_by(sort_criteria).paginate(page=page, per_page=PAGINATION)
    else:
        list = my_query.order_by(desc(sort_criteria)).paginate(page=page, per_page=PAGINATION)
    args_filter_and_sort = {**args_filter, **args_sort}
    return render_template('rents.html', form=form, rents_list=list, extra_filter_args=args_filter, extra_sort_and_filter_args=args_filter_and_sort, count_filtered = count_filtered)
