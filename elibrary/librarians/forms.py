from datetime import date, timedelta
from flask_wtf import FlaskForm#, RecaptchaField
from flask_babel import lazy_gettext as _l
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, DateField
from wtforms.validators import ValidationError
from elibrary.models import Librarian
from elibrary.utils.numeric_defines import REGISTRATION_DATE_LIMIT
from elibrary.utils.custom_validations import (required_cust, email_cust, required_cust_date,
        phone_cust, string_cust, username_cust, equal_to_cust, length_cust, optional_cust)


class LoginForm(FlaskForm):
    username = StringField(_l('Username'), validators=[required_cust(), username_cust()])
    password = PasswordField(_l('Password'), validators=[required_cust()])
    submit = SubmitField(_l('Login'))

class LibrarianBaseForm(FlaskForm):
    first_name = StringField(_l('First name'), validators=[required_cust(), length_cust(max=20), string_cust()])
    last_name = StringField(_l('Last name'), validators=[required_cust(), length_cust(max=40), string_cust()])

class LibrarianForm(LibrarianBaseForm):
    email = StringField(_l('E-mail'), validators=[optional_cust(), email_cust()])
    phone_1 = StringField(_l('Phone number'), validators=[required_cust(), phone_cust()])
    phone_2 = StringField(_l('Second phone number'), validators=[optional_cust(), phone_cust()])
    address = StringField(_l('Address'), validators=[required_cust(), length_cust(max=50), string_cust()])
    town = StringField(_l('Town'), validators=[required_cust(), length_cust(max=20), string_cust()])

    def validate_username(self, username):
        librarian = Librarian.query.filter_by(username=username.data).first()
        if librarian:
            raise ValidationError(_l('That username is taken. Please choose a different one')+'.')

class LibrarianCreateForm(LibrarianForm):
    date_registered = DateField(_l('Registration date'), validators=[required_cust_date()], format='%d.%m.%Y.', default=date.today)
    username = StringField(_l('Username'), validators=[required_cust(), length_cust(min=6, max=30), username_cust()])
    password = PasswordField(_l('Password'), validators=[required_cust(), length_cust(min=6)])
    confirm_password = PasswordField(_l('Confirm password'), validators=[required_cust(), equal_to_cust('password')])
    is_administrator = BooleanField(_l('This will be library administrator account'), validators=[optional_cust()])
    submit = SubmitField(_l('Add librarian'))

    def validate_date_registered(self, date_registered):
        if date_registered.data > date.today():
            raise ValidationError(_l('Registration date can not be set in future') + '.')
        elif date_registered.data < date.today() - timedelta(REGISTRATION_DATE_LIMIT):
            raise ValidationError(_l('Registration date can be set in past for more than') + ' ' + str(REGISTRATION_DATE_LIMIT) + ' ' + _l('days') + '.')

class LibrarianUpdateForm(LibrarianForm):
    username = StringField(_l('Username'), validators=[optional_cust(), length_cust(min=6, max=30), username_cust()])
    submit = SubmitField(_l('Update librarian'))


class LibrarianRequestChangePasswordForm(LibrarianBaseForm):
    username = StringField(_l('Username'), validators=[required_cust(), length_cust(min=6, max=30), username_cust()])
    submit = SubmitField(_l('Request password change'))


class LibrarianChangePasswordForm(FlaskForm):
    new_password = PasswordField(_l('Password'), validators=[required_cust(), length_cust(min=6)])
    confirm_password = PasswordField(_l('Confirm password'), validators=[required_cust(), equal_to_cust('new_password')])
    submit = SubmitField(_l('Update password'))

class LibrarianUpdatePasswordForm(LibrarianChangePasswordForm):
    old_password = PasswordField(_l('Old password'), validators=[required_cust(), length_cust(min=6)])
