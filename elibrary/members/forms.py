from datetime import date, timedelta
from flask_wtf import FlaskForm
from flask_babel import gettext, lazy_gettext as _l
from wtforms import StringField, SubmitField, SelectField, IntegerField, DateField, TextAreaField
from wtforms.validators import ValidationError
from elibrary.models import Member
from elibrary.utils.defines import BACKWARD_INPUT_LIMIT, DATE_FORMAT
from elibrary.utils.custom_validations import (required_cust, email_cust, required_cust_date,
        phone_cust, string_cust, username_cust, equal_to_cust, length_cust, optional_cust)

class UserForm(FlaskForm):
    first_name = StringField(_l('First name'), validators=[required_cust(), length_cust(max=20), string_cust()])
    last_name = StringField(_l('Last name'), validators=[required_cust(), length_cust(max=30), string_cust()])
    father_name = StringField(_l('Father name'), validators=[required_cust(), length_cust(max=20), string_cust()])
    profession = StringField(_l('Profession'), validators=[required_cust(), length_cust(max=50), string_cust()])
    email = StringField(_l('E-mail address'), validators=[optional_cust(), email_cust(), length_cust(max=50)])
    phone = StringField(_l('Phone'), validators=[required_cust(), phone_cust()])
    address = StringField(_l('Address'), validators=[required_cust(), length_cust(max=60), string_cust()])

class MemberCreateForm(UserForm):
    date_registered = DateField(_l('Registration date'), validators=[required_cust_date()], format=DATE_FORMAT, default=date.today())
    submit = SubmitField(_l('Add member'))

    def validate_date_registered(self, date_registered):
        if date_registered.data > date.today():
            raise ValidationError(_l('Date can not be set in future') + '.')
        elif date_registered.data < date.today() - timedelta(BACKWARD_INPUT_LIMIT):
            raise ValidationError(_l('Date cannot be set in past for more than') + ' ' + str(BACKWARD_INPUT_LIMIT) + ' ' + _l('days') + '.')

class MemberUpdateForm(UserForm):
    submit = SubmitField(_l('Update member'))

class FilterForm(FlaskForm):
    registration_date_from = StringField(_l('Registered after'))
    registration_date_to = StringField(_l('Registered before'))
    expiration_date_from = StringField(_l('Membership expires after'))
    expiration_date_to = StringField(_l('Membership expires before'))
    books_rented_from = IntegerField(_l('Number of rented books above'))
    books_rented_to = IntegerField(_l('Number of rented books below'))
    id = StringField(_l('Member id'))
    first_name = StringField(_l('First name'))
    last_name = StringField(_l('Last name'))
    has_rented_books = SelectField(_l('Has currently rented books'), choices=[('none', _l('Not selected')), ('yes', _l('Yes')), ('no', _l('No'))])
    has_expired = SelectField(_l('Membership status'), choices=[('no_option', _l('Not selected')), ('expired', _l('Membership expired')), ('near_expiration', _l('Membership near expiration')), ('active', _l('Membership active'))])
    submit = SubmitField(_l('Filter'))

class ShortFilterForm(FlaskForm):
    text = StringField(_l('Search for'), validators=[length_cust(max=40), string_cust()])
    submit = SubmitField(_l('Search'))
