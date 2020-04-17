from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, SubmitField
from elibrary.utils.custom_validations import optional_cust, string_cust, length_cust, signature_cust, numeric_cust

class FilterForm(FlaskForm):
    inv_number = StringField(_l('Inventory number'))
    signature = StringField(_l('Signature'))
    title = StringField(_l('Title'))
    author = StringField(_l('Author'))
    submit = SubmitField(_l('Submit'))

class SearchForm(FlaskForm):
    text = StringField(_l('Search for'), validators=[optional_cust(), string_cust(), length_cust(max=50)])
    submit = SubmitField(_l('Submit'))

class BookUpdateForm(FlaskForm):
    inv_number = StringField(_l('Inventory number'), validators=[optional_cust(), numeric_cust(), length_cust(max=6)])
    signature = StringField(_l('Signature'), validators=[optional_cust(), signature_cust(), length_cust(max=15)])
    title = StringField(_l('Title'), validators=[optional_cust(), string_cust(), length_cust(max=50)])
    author = StringField(_l('Author'), validators=[optional_cust(), string_cust(), length_cust(max=50)])
    submit = SubmitField(_l('Submit'))
