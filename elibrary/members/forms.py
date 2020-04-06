from datetime import date, timedelta
from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, SubmitField, SelectField, IntegerField, DateField
from wtforms.validators import ValidationError
from elibrary.models import Member
from elibrary.utils.common import Common
from elibrary.utils.numeric_defines import REGISTRATION_DATE_LIMIT, MAXIMUM_USER_YEARS, MINIMUM_USER_YEARS
from elibrary.utils.custom_validations import (required_cust, email_cust, required_cust_date,
        phone_cust, string_cust, username_cust, equal_to_cust, length_cust, optional_cust)

class UserForm(FlaskForm):
    first_name = StringField(_l('First name'), validators=[required_cust(), length_cust(max=20), string_cust()])
    last_name = StringField(_l('Last name'), validators=[required_cust(), length_cust(max=40), string_cust()])
    email = StringField(_l('E-mail'), validators=[optional_cust(), email_cust()])
    phone_1 = StringField(_l('Phone number'), validators=[required_cust(), phone_cust()])
    phone_2 = StringField(_l('Second phone number'), validators=[optional_cust(), phone_cust()])
    address = StringField(_l('Address'), validators=[required_cust(), length_cust(max=50), string_cust()])
    town = StringField(_l('Town'), validators=[required_cust(), length_cust(max=20), string_cust()])
    birth_date = DateField(_l('Birth date'), validators=[required_cust_date()], format='%d.%m.%Y.')

    def validate_birth_date(self, birth_date):
        today = date.today()
        min_value = date(today.year - MAXIMUM_USER_YEARS, today.month, today.day)
        max_value = date(today.year - MINIMUM_USER_YEARS, today.month, today.day)
        if birth_date.data > today:
            raise ValidationError(_l('Birth date can not be set in future') + '.')
        elif birth_date.data > max_value:
            raise ValidationError(_l('New member can not have less than') + ' '+ str(MINIMUM_USER_YEARS) + ' ' + _l('years') + '. ' + _l('Value must be less than') + ' ' + max_value.strftime('%d.%m.%Y.'))
        elif birth_date.data < min_value:
            raise ValidationError(_l('New member can not have more than') + ' '+ str(MAXIMUM_USER_YEARS) + ' ' + _l('years') + '. ' + _l('Value must be at least') + ' ' + min_value.strftime('%d.%m.%Y.'))


class MemberCreateForm(UserForm):
    label = StringField(_l('Label'), validators=[required_cust(), length_cust(max=15), string_cust()])
    date_registered = DateField(_l('Registration date'), validators=[required_cust_date()], format='%d.%m.%Y.', default=date.today)
    submit = SubmitField(_l('Add member'))

    def validate_date_registered(self, date_registered):
        if date_registered.data > date.today():
            raise ValidationError(_l('Registration date can not be set in future') + '.')
        elif date_registered.data < date.today() - timedelta(REGISTRATION_DATE_LIMIT):
            raise ValidationError(_l('Registration date can be set in past for more than') + ' ' + str(REGISTRATION_DATE_LIMIT) + ' ' + _l('days') + '.')

    def validate_label(self, label):
        member = Member.query.filter_by(label=label.data).first()
        if member:
            raise ValidationError(_l('That label is already in use. Please choose a different one')+'.')

class MemberUpdateForm(UserForm):
    submit = SubmitField(_l('Update member'))

class UserExtensionForm(FlaskForm):
    extension_date = DateField(_l('Extend membership to the following date'), validators=[required_cust_date()], format='%d.%m.%Y.')
    submit = SubmitField(_l('Extend membership'))
    maximum_date = date.today()
    fixed_value = False

    def validate_extension_date(self, extension_date):
        if self.fixed_value and not extension_date.data == self.maximum_date:
            raise ValidationError(_l('This user membership extension date must be set to') + ' ' + self.maximum_date.strftime('%d.%m.%Y.'))
        elif extension_date.data > self.maximum_date:
            raise ValidationError(_l('Membership for this user can not be set after the') + ' ' + self.maximum_date.strftime('%d.%m.%Y.'))
        elif extension_date.data < self.maximum_date - timedelta(REGISTRATION_DATE_LIMIT):
            raise ValidationError(_l('Membership for this user can not be set before the') + ' ' + (self.maximum_date - timedelta(REGISTRATION_DATE_LIMIT)).strftime('%d.%m.%Y.'))

class FilterForm(FlaskForm):
    registration_date_from = StringField(_l('Registered after'))
    registration_date_to = StringField(_l('Registered before'))
    expiration_date_from = StringField(_l('Membership expires after'))
    expiration_date_to = StringField(_l('Membership expires before'))
    birth_date_from = StringField(_l('Birth date after'))
    birth_date_to = StringField(_l('Birth date before'))
    books_rented_from = IntegerField(_l('Number of rented books, equan and above'))
    books_rented_to = IntegerField(_l('Number of rented books, equan and below'))
    label = StringField(_l('Label'))
    first_name = StringField(_l('First name'))
    last_name = StringField(_l('Last name'))
    has_rented_books = SelectField(_l('Has currently rented books'), choices=[('no_option', '('+_l('Not selected')+')'), ('has_rented', _l('Yes')), ('does_not_have', _l('No'))])
    has_expired = SelectField(_l('Membership status'), choices=[('no_option', '('+_l('Not selected')+')'), ('expired', _l('Membership expired')), ('near_expiration', _l('Membership near expiration')), ('active', _l('Membership active'))])
    submit = SubmitField(_l('Filter'))

class ShortFilterForm(FlaskForm):
    text = StringField(_l('Search for'), validators=[length_cust(max=40), string_cust()])
    submit = SubmitField(_l('Search'))
