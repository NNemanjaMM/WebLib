from datetime import date, timedelta
from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, SubmitField, SelectField, IntegerField, TextAreaField, DateField
from wtforms.validators import ValidationError
from elibrary.utils.numeric_defines import REGISTRATION_DATE_LIMIT, MAXIMUM_USER_YEARS, MINIMUM_USER_YEARS
from elibrary.utils.custom_validations import (required_cust, email_cust,
        phone_cust, string_cust, username_cust, equal_to_cust, length_cust, optional_cust)


class UserForm(FlaskForm):
    first_name = StringField(_l('First name'), validators=[required_cust(), length_cust(max=20), string_cust()])
    last_name = StringField(_l('Last name'), validators=[required_cust(), length_cust(max=40), string_cust()])
    email = StringField(_l('E-mail'), validators=[optional_cust(), email_cust()])
    phone_1 = StringField(_l('Phone number'), validators=[required_cust(), phone_cust()])
    phone_2 = StringField(_l('Second phone number'), validators=[optional_cust(), phone_cust()])
    address = StringField(_l('Address'), validators=[required_cust(), length_cust(max=50), string_cust()])
    town = StringField(_l('Town'), validators=[required_cust(), length_cust(max=20), string_cust()])
    birth_year = IntegerField(_l('Year of birth'), validators=[optional_cust()])

    def validate_birth_year(self, birth_year):
        if birth_year.data:
            min_value = int(date.today().year) - MAXIMUM_USER_YEARS
            max_value = int(date.today().year) - MINIMUM_USER_YEARS
            if birth_year.data > max_value:
                raise ValidationError(_l('New member can not have less than') + ' '+ MINIMUM_USER_YEARS + ' ' + _l('years') + '. ' + _l('Value must be less than') + ' ' + str(max_value) + '.')
            elif birth_year.data < min_value:
                raise ValidationError(_l('New member can not have more than') + ' '+ MAXIMUM_USER_YEARS + ' ' + _l('years') + '. ' + _l('Value must be at least') + ' ' + str(min_value) + '.')

class MemberCreateForm(UserForm):
    date_registered = DateField(_l('Registration date'), validators=[optional_cust()], format='%d.%m.%Y.', default=date.today)
    submit = SubmitField(_l('Add member'))

    def validate_date_registered(self, date_registered):
        if not date_registered.data:
            raise ValidationError(_l('Date value is not valid') + '. ' + _l('Make sute if matches the following format "dd.mm.yyyy."') +'.')
        elif date_registered.data > date.today():
            raise ValidationError(_l('Registration date can not be set in future') + '.')
        elif date_registered.data < date.today() - timedelta(REGISTRATION_DATE_LIMIT):
            raise ValidationError(_l('Registration date can be set in past for more than') + ' ' + REGISTRATION_DATE_LIMIT + ' ' + _l('days') + '.')

class MemberUpdateForm(UserForm):
    submit = SubmitField(_l('Update member'))
