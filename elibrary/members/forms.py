from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, SubmitField, SelectField, IntegerField, TextAreaField
from wtforms.validators import ValidationError
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

class MemberCreateForm(UserForm):
    submit = SubmitField(_l('Add member'))

class MemberUpdateForm(UserForm):
    submit = SubmitField(_l('Update member'))
