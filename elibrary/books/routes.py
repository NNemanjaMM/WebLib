from datetime import date, timedelta
from flask import render_template, url_for, request, flash, redirect, abort, Blueprint
from flask_login import login_required, current_user
from flask_babel import gettext, lazy_gettext as _l
from elibrary import db
from elibrary.models import Book, Member, Rental
from elibrary.utils.defines import PAGINATION, MAX_RENTED_BOOKS, RENTAL_DATE_LIMIT, DATE_FORMAT
from elibrary.utils.custom_validations import string_cust, length_cust_max, numeric_cust, signature_cust, length_cust_max_15, FieldValidator
from elibrary.books.forms import FilterForm, SearchForm, BookCreateUpdateForm, BookRentForm, BookRentTerminationForm
from sqlalchemy import desc, or_, and_, func

books = Blueprint('books', __name__)

@books.route("/books")
@login_required
def bookss(filtering = False, searching = False):
    page = request.args.get('page', 1, type=int)
    sort_criteria = request.args.get('sort_by', 'inv_number', type=str)
    sort_direction = request.args.get('direction', 'up', type=str)
    args_sort = {'sort_by': sort_criteria, 'direction': sort_direction}
    if not (sort_criteria == 'inv_number' or sort_criteria == 'signature' or sort_criteria == 'title' or sort_criteria == 'author'):
        sort_criteria = 'inv_number'

    s_text = request.args.get('text')
    f_inv_number = request.args.get('inv_number')
    f_signature = request.args.get('signature')
    f_title = request.args.get('title')
    f_author = request.args.get('author')
    if filtering:
        s_text = None
    elif searching:
        f_inv_number = None
        f_signature = None
        f_title = None
        f_author = None

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
        if not (f_inv_number == None or f_inv_number == ""):
            form.inv_number.data = f_inv_number
            if FieldValidator.validate_field(form, form.inv_number, [numeric_cust, length_cust_max]):
                my_query = my_query.filter(Book.inv_number.like('%' + f_inv_number + '%'))
                args_filter['inv_number'] = f_inv_number
            else:
                filter_has_errors = True

        if not (f_signature == None or f_signature == ""):
            form.signature.data = f_signature
            if FieldValidator.validate_field(form, form.signature, [signature_cust, length_cust_max]):
                my_query = my_query.filter(Book.signature.like('%' + f_signature + '%'))
                args_filter['signature'] = f_signature
            else:
                filter_has_errors = True

        if not (f_title == None or f_title == ""):
            form.title.data = f_title
            if FieldValidator.validate_field(form, form.title, [string_cust, length_cust_max]):
                my_query = my_query.filter(Book.title.like('%' + f_title + '%'))
                args_filter['title'] = f_title
            else:
                filter_has_errors = True

        if not (f_author == None or f_author == ""):
            form.author.data = f_author
            if FieldValidator.validate_field(form, form.author, [string_cust, length_cust_max]):
                my_query = my_query.filter(Book.author.like('%' + f_author + '%'))
                args_filter['author'] = f_author
            else:
                filter_has_errors = True

    if filter_has_errors:
        flash(_l('There are filter values with errors')+'. '+_l('However, valid filter values are applied')+'.', 'warning')
    if sort_direction == 'up':
        list = my_query.order_by(sort_criteria).paginate(page=page, per_page=PAGINATION)
    else:
        list = my_query.order_by(desc(sort_criteria)).paginate(page=page, per_page=PAGINATION)
    args_filter_and_sort = {**args_filter, **args_sort}
    return render_template('books.html', form=form, form2=form2, books_list=list, extra_filter_args=args_filter, extra_sort_and_filter_args=args_filter_and_sort)

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
        db.session.commit()
        flash(_l('Book is successfuly updated')+'.', 'success')
        return redirect(url_for('books.bookss'))
    elif request.method == 'GET':
        form.inv_number.data = book.inv_number
        form.signature.data = book.signature
        form.title.data = book.title
        form.author.data = book.author
    return render_template('books_cu.html', form=form, title=_l('Update book'))

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
        db.session.add(book)
        db.session.commit()
        flash(_l('Book is successfuly added')+'.', 'success')
        if book_duplicate:
            flash(_l('Book with the same inventory number already exists')+'!', 'warning')
        return redirect(url_for('books.bookss'))
    return render_template('books_cu.html', form=form, title=_l('Add book'))

@books.route("/books/rent/<int:member_id>", methods=['GET', 'POST'])
@login_required
def book_rent(member_id):
    member = Member.query.get_or_404(member_id)
    if member.is_membership_expired or member.number_of_rented_books >= MAX_RENTED_BOOKS:
        abort(405)
    message = None
    form = BookRentForm()
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
            rental.book_id = book_id
            rental.member_id = member_id
            rental.librarian_rent_id = current_user.id
            db.session.add(rental)
            member.number_of_rented_books = db.session.query(func.count(Rental.id)).filter(and_(Rental.member_id == member_id, Rental.is_terminated == False)).scalar()
            member.total_books_rented = db.session.query(func.count(Rental.id)).filter(Rental.member_id == member_id).scalar()
            db.session.commit()
            flash(_l('Book is successfuly rented')+'.', 'info')
            return redirect(url_for('members.members_details', member_id=member_id))
    return render_template('renting.html', form=form, message=message)

@books.route("/books/rents")
@login_required
def book_rents():
    page = request.args.get('page', 1, type=int)
    sort_criteria = request.args.get('sort_by', 'id', type=str)
    sort_direction = request.args.get('direction', 'up', type=str)
    args_sort = {'sort_by': sort_criteria, 'direction': sort_direction}

    filter_has_errors = False
    args_filter = {}
    form = FilterForm()
    form2 = SearchForm()
    my_query = db.session.query(Rental)

    if filter_has_errors:
        flash(_l('There are filter values with errors')+'. '+_l('However, valid filter values are applied')+'.', 'warning')
    if sort_direction == 'up':
        list = my_query.order_by(sort_criteria).paginate(page=page, per_page=PAGINATION)
    else:
        list = my_query.order_by(desc(sort_criteria)).paginate(page=page, per_page=PAGINATION)
    args_filter_and_sort = {**args_filter, **args_sort}
    return render_template('rents.html', form=form, form2=form2, rents_list=list, extra_filter_args=args_filter, extra_sort_and_filter_args=args_filter_and_sort)


@books.route("/books/rents/<int:rent_id>", methods=['GET', 'POST'])
@login_required
def book_rents_details(rent_id):
    rent = Rental.query.get_or_404(rent_id)
    member = Member.query.get_or_404(rent.member_id)
    form = BookRentTerminationForm()
    form.date_rented = rent.date_performed
    if not rent.is_terminated and form.validate_on_submit():
        rent.is_terminated = True
        rent.date_termination = form.date_returned.data
        rent.librarian_return_id = current_user.id
        member.number_of_rented_books = db.session.query(func.count(Rental.id)).filter(and_(Rental.member_id == member.id, Rental.is_terminated == False)).scalar()
        db.session.commit()
    return render_template('rent.html', form=form, rent=rent)
