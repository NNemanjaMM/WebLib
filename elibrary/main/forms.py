from flask_wtf import FlaskForm
from flask_babel import gettext as _l
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, optional

class AcceptRejectForm(FlaskForm):
    approve = SubmitField(_l('Approve'))
    reject = SubmitField(_l('Reject'))
