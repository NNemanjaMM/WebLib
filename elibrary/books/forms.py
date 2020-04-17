#from datetime import date, timedelta
#from sqlalchemy import and_
from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, SubmitField#, DateField, TextAreaField, DecimalField, BooleanField#,SelectField, IntegerField
#from wtforms.ext.sqlalchemy.fields import QuerySelectField
#from wtforms.validators import ValidationError
#from elibrary.models import ExtensionPrice#,Member
#from elibrary.utils.common import Common
#from elibrary.utils.defines import REGISTRATION_DATE_LIMIT, DATE_FORMAT
from elibrary.utils.custom_validations import optional_cust, string_cust, length_cust, signature_cust, numeric_cust# required_cust, char_cust, required_cust_decimal
#        phone_cust, username_cust, equal_to_cust, required_cust, email_cust, required_cust_date)



class FilterForm(FlaskForm):
    inv_number = StringField(_l('Inventory number'), validators=[optional_cust(), numeric_cust(), length_cust(max=6)])
    signature = StringField(_l('Signature'), validators=[optional_cust(), signature_cust(), length_cust(max=15)])
    title = StringField(_l('Title'), validators=[optional_cust(), string_cust(), length_cust(max=50)])
    author = StringField(_l('Author'), validators=[optional_cust(), string_cust(), length_cust(max=50)])
    submit = SubmitField(_l('Submit'))


class SearchForm(FlaskForm):
    text = StringField(_l('Search for'), validators=[optional_cust(), string_cust(), length_cust(max=50)])
    submit = SubmitField(_l('Submit'))
