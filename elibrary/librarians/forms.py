from flask_wtf import FlaskForm#, RecaptchaField
from flask_babel import lazy_gettext as _l
from flask_login import current_user
from wtforms import StringField, PasswordField, SubmitField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, optional, ValidationError
from elibrary.models import Librarian

# TODO popuniti poruke za sve validatore

class LoginForm(FlaskForm):
    username = StringField(_l('Username'), validators=[DataRequired()])
    password = PasswordField(_l('Password'), validators=[DataRequired()])
    submit = SubmitField(_l('Login'))

class LibrarianBaseForm(FlaskForm):
    first_name = StringField(_l('First name'), validators=[DataRequired(message=_l('The field must be filled')+'.'), Length(max=20)])
    last_name = StringField(_l('Last name'), validators=[DataRequired(), Length(max=40)])

class LibrarianForm(LibrarianBaseForm):
    email = StringField(_l('E-mail'), validators=[optional(), Email(message=_l('Value does not match e-mail format'+'.'))])
    phone_1 = StringField(_l('Phone number'), validators=[DataRequired(), Length(max=15)])
    phone_2 = StringField(_l('Second phone number'), validators=[optional(), Length(max=15)])
    address = StringField(_l('Address'), validators=[DataRequired(), Length(max=50)])
    town = StringField(_l('Town'), validators=[DataRequired(), Length(max=20)])

    def validate_username(self, username):
        librarian = Librarian.query.filter_by(username=username.data).first()
        if librarian:
            raise ValidationError(_l('That username is taken. Please choose a different one')+'.')

class LibrarianCreateForm(LibrarianForm):
    username = StringField(_l('Username'), validators=[DataRequired(), Length(min=6, max=30)])
    password = PasswordField(_l('Password'), validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(_l('Confirm password'), validators=[DataRequired(), EqualTo('password')])
    is_administrator = BooleanField(_l('This will be library administrator account'), validators=[optional()])
    submit = SubmitField(_l('Add librarian'))
#    recaptcha = RecaptchaField()

class LibrarianUpdateForm(LibrarianForm):
    username = StringField(_l('Username'), validators=[optional(), Length(min=6, max=30)])
    submit = SubmitField(_l('Update librarian'))


class LibrarianRequestChangePasswordForm(LibrarianBaseForm):
    username = StringField(_l('Username'), validators=[DataRequired(), Length(min=6, max=30)])
    submit = SubmitField(_l('Request password change'))


class LibrarianChangePasswordForm(FlaskForm):
    new_password = PasswordField(_l('New password'), validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField(_l('Confirm password'), validators=[DataRequired(), EqualTo('new_password', message=_l('Confirm password value does not match new password value')+'.')])
    submit = SubmitField(_l('Update password'))

class LibrarianUpdatePasswordForm(LibrarianChangePasswordForm):
    old_password = PasswordField(_l('Old password'), validators=[DataRequired(), Length(min=6)])

class AcceptForm(FlaskForm):
    submit_accept = SubmitField(_l('Approve'))

class RejectForm(FlaskForm):
    submit_reject = SubmitField(_l('Reject'))
