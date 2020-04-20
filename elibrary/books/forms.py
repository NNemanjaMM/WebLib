from datetime import date, timedelta
from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, SubmitField, DateField
from wtforms.validators import ValidationError
from elibrary.utils.custom_validations import optional_cust, required_cust, required_cust_date, string_cust, length_cust, signature_cust, numeric_cust
from elibrary.utils.defines import DATE_FORMAT, BACKWARD_INPUT_LIMIT

class FilterForm(FlaskForm):
    inv_number = StringField(_l('Inventory number'))
    signature = StringField(_l('Signature'))
    title = StringField(_l('Title'))
    author = StringField(_l('Author'))
    submit = SubmitField(_l('Filter'))

class SearchForm(FlaskForm):
    text = StringField(_l('Search for'), validators=[optional_cust(), string_cust(), length_cust(max=50)])
    submit = SubmitField(_l('Search'))

class BookCreateUpdateForm(FlaskForm):
    inv_number = StringField(_l('Inventory number'), validators=[required_cust(), numeric_cust(), length_cust(max=6)])
    signature = StringField(_l('Signature'), validators=[required_cust(), signature_cust(), length_cust(max=15)])
    title = StringField(_l('Title'), validators=[required_cust(), string_cust(), length_cust(max=50)])
    author = StringField(_l('Author'), validators=[required_cust(), string_cust(), length_cust(max=50)])
    submit = SubmitField(_l('Submit'))

class BookRentForm(FlaskForm):
    date_rented = StringField(_l('Rent date'))
    inv_number = StringField(_l('Inventory number'))
    signature = StringField(_l('Signature'))
    title = StringField(_l('Title'))
    author = StringField(_l('Author'))
    submit = SubmitField(_l('Submit'))
    search = SubmitField(_l('Search'))

class BookRentTerminationForm(FlaskForm):
    date_rented = None
    date_returned = DateField(_l('Book return date'), validators=[required_cust_date()], format=DATE_FORMAT)
    submit = SubmitField(_l('Submit'))

    def validate_date_returned(self, date_returned):
        if date_returned.data > date.today():
            raise ValidationError(_l('Book return date') + ' '+ _l('cannot be set in future') + '.')
        elif date_returned.data < date.today() - timedelta(BACKWARD_INPUT_LIMIT):
            raise ValidationError(_l('Book return date') + ' '+ _l('cannot be set in past for more than') + ' ' + str(BACKWARD_INPUT_LIMIT) + ' ' + _l('days') + '.')
        elif date_returned.data < self.date_rented:
            raise ValidationError(_l('Book cannot be returned after its rental') + '.')
