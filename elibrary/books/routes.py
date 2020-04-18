from flask import render_template, url_for, request, flash, redirect, Blueprint
from flask_login import login_required
from flask_babel import gettext, lazy_gettext as _l
from elibrary import db
from elibrary.models import Book
from elibrary.utils.defines import PAGINATION
from elibrary.utils.custom_validations import string_cust, length_cust_max, numeric_cust, signature_cust, FieldValidator
from elibrary.books.forms import FilterForm, SearchForm, BookCreateUpdateForm
from sqlalchemy import desc, or_

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
