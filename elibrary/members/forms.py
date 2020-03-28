from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, SubmitField, SelectField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, optional

class UserForm(FlaskForm):
    first_name = StringField(_l('First name'), validators=[DataRequired(), Length(max=20)])
    last_name = StringField(_l('Last name'), validators=[DataRequired(), Length(max=40)])
    email = StringField(_l('E-mail'), validators=[optional(), Email()])
    phone_1 = StringField(_l('Phone number'), validators=[DataRequired(), Length(max=15)])
    phone_2 = StringField(_l('Second phone number'), validators=[optional(), Length(max=15)])
    address = StringField(_l('Address'), validators=[DataRequired(), Length(max=50)])
    town = StringField(_l('Town'), validators=[DataRequired(), Length(max=20)])
    birth_year = IntegerField(_l('Year of birth'), validators=[optional()])

class MemberCreateForm(UserForm):
    submit = SubmitField(_l('Add member'))

class MemberUpdateForm(UserForm):
    submit = SubmitField(_l('Update member'))
