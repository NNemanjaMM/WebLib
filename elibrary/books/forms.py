from datetime import date, timedelta
from flask_wtf import FlaskForm
from flask_babel import gettext, lazy_gettext as _l
from wtforms import StringField, SubmitField, DateField, SelectField, BooleanField
from wtforms.validators import ValidationError
from elibrary.models import Book
from elibrary.utils.custom_validations import optional_cust, required_cust, required_cust_date, string_cust, length_cust, signature_cust, numeric_cust
from elibrary.utils.defines import DATE_FORMAT, BACKWARD_INPUT_LIMIT

class FilterForm(FlaskForm):
    inv_number = StringField(_l('Inventory number'))
    signature = StringField(_l('Signature'))
    title = StringField(_l('Title'))
    author = StringField(_l('Author'))
    is_rented = SelectField(_l('Is rented'), choices=[('none', _l('Not selected')), ('yes', _l('Yes')), ('no', _l('No'))])
    has_error = SelectField(_l('Has error'), choices=[('none', _l('Not selected')), ('yes', _l('Yes')), ('no', _l('No'))])
    submit = SubmitField(_l('Filter'))

class SearchForm(FlaskForm):
    text = StringField(_l('Search for'), validators=[optional_cust(), string_cust(), length_cust(max=50)])
    submit = SubmitField(_l('Search'))

class BookCUForm(FlaskForm):
    inv_number = StringField(_l('Inventory number'), validators=[required_cust(), numeric_cust(), length_cust(max=6)])
    signature = StringField(_l('Signature'), validators=[required_cust(), signature_cust(), length_cust(max=15)])
    title = StringField(_l('Title'), validators=[required_cust(), string_cust(), length_cust(max=50)])
    author = StringField(_l('Author'), validators=[required_cust(), string_cust(), length_cust(max=50)])
    has_error = BooleanField(_l('Has error') + ' (' + _l('book has a problematic inventory number') + ')')

class BookUpdateForm(BookCUForm):
    submit = SubmitField(_l('Update book'))

class BookCreateForm(BookCUForm):
    submit = SubmitField(_l('Add book'))
    def validate_inv_number(self, inv_number):
        book_duplicate = Book.query.filter(Book.inv_number==inv_number.data).first()
        if book_duplicate:
            raise ValidationError(_l('Book with this inventory number') + ' ' +_l('already exists'))

class RentForm(FlaskForm):
    date_rented = StringField(_l('Rent date'))
    inv_number = StringField(_l('Inventory number'))
    signature = StringField(_l('Signature'))
    title = StringField(_l('Title'))
    author = StringField(_l('Author'))
    submit = SubmitField(_l('Rent book'))
    search = SubmitField(_l('Search'))

class RentTerminationForm(FlaskForm):
    date_rented = None
    date_returned = DateField(_l('Return date'), validators=[required_cust_date()], format=DATE_FORMAT)
    submit = SubmitField(_l('Return book'))

    def validate_date_returned(self, date_returned):
        if date_returned.data > date.today():
            raise ValidationError(_l('Date can not be set in future') + '.')
        elif date_returned.data < date.today() - timedelta(BACKWARD_INPUT_LIMIT):
            raise ValidationError(_l('Date cannot be set in past for more than') + ' ' + str(BACKWARD_INPUT_LIMIT) + ' ' + _l('days') + '.')
        elif date_returned.data < self.date_rented:
            raise ValidationError(_l('Return date can not be set before rent date') + '.')

class RentFilterForm(FlaskForm):
    book_id = StringField(_l('Book id'))
    member_id = StringField(_l('Member id'))
    is_terminated = SelectField(_l('Is returned'), choices=[('none', _l('Not selected')), ('yes', _l('Yes')), ('no', _l('No'))])
    is_deadlime_passed = SelectField(_l('Is deadline passed'), choices=[('none', _l('Not selected')), ('yes', _l('Yes')), ('no', _l('No'))])
    date_performed_from = StringField(_l('Rent date after'))
    date_performed_to = StringField(_l('Rent date before'))
    date_deadline_from = StringField(_l('Deadline date after'))
    date_deadline_to = StringField(_l('Deadline date before'))
    date_terminated_from = StringField(_l('Returned date after'))
    date_terminated_to = StringField(_l('Returned date before'))
    submit = SubmitField(_l('Filter'))
