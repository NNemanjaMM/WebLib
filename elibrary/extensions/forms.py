from datetime import date, timedelta
from sqlalchemy import and_
from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, SubmitField, DateField, TextAreaField, DecimalField, BooleanField
from wtforms.ext.sqlalchemy.fields import QuerySelectField
from wtforms.validators import ValidationError
from elibrary.models import ExtensionPrice
from elibrary.utils.defines import BACKWARD_INPUT_LIMIT, DATE_FORMAT
from elibrary.utils.custom_validations import (optional_cust, string_cust, length_cust, required_cust, required_cust_date, char_cust, required_cust_decimal)

class ExtensionForm(FlaskForm):
    price = QuerySelectField(_l('Price'), query_factory=lambda: ExtensionPrice.query.filter_by(is_enabled=True).order_by(ExtensionPrice.price_value))
    note = TextAreaField(_l('Note'), validators=[optional_cust(), string_cust(), length_cust(max=150)])
    date_performed = DateField(_l('Extension performed on'), validators=[required_cust_date()], format=DATE_FORMAT, default=date.today())
    submit = SubmitField(_l('Extend membership'))

    def validate_date_performed(self, date_performed):
        if date_performed.data > date.today():
            raise ValidationError(_l('Extension date') + ' '+ _l('cannot be set in future') + '.')
        elif date_performed.data < date.today() - timedelta(BACKWARD_INPUT_LIMIT):
            raise ValidationError(_l('Extension date') + ' '+ _l('cannot be set in past for more than') + ' ' + str(BACKWARD_INPUT_LIMIT) + ' ' + _l('days') + '.')

    def validate_price(self, price):
        if not price.data == None:
            found = ExtensionPrice.query.filter_by(id=price.data.id).first()
            if not found:
                raise ValidationError(_l('Price value is not valid') + '.')

class FilterForm(FlaskForm):
    date_performed_from = StringField(_l('Expanded after'))
    date_performed_to = StringField(_l('Expanded before'))
    date_extended_from = StringField(_l('Membership expires after'))
    date_extended_to = StringField(_l('Membership expires before'))
    price = QuerySelectField(_l('Price'), query_factory=lambda: ExtensionPrice.query.order_by(ExtensionPrice.price_value), allow_blank=True, blank_text=_l('Not selected'))
    member_id = StringField(_l('Member id'))
    submit = SubmitField(_l('Filter'))

class PriceUpdate(FlaskForm):
    note = TextAreaField(_l('Add a note'), validators=[optional_cust(), string_cust(), length_cust(max=150)])
    submit = SubmitField(_l('Submit'))

class PriceAdd(FlaskForm):
    price_value = DecimalField(_l('Price'), validators=[required_cust_decimal()], places=2)
    currency = StringField(_l('Currency'), validators=[required_cust(), char_cust(), length_cust(max=3)])
    note = TextAreaField(_l('Note'), validators=[optional_cust(), string_cust(), length_cust(max=150)])
    is_enabled = BooleanField(_l('Enable price upon creation'))
    submit = SubmitField(_l('Submit'))

    def validate_price_value(self, price_value):
        if price_value.data < 0.0:
            raise ValidationError(_l('Price value can not be lower than zero')+'.')
        elif price_value.data > 100.0:
            raise ValidationError(_l('Price value can not be higher than hundred')+'.')
        else:
            exists = ExtensionPrice.query.filter(and_(ExtensionPrice.price_value==price_value.data, ExtensionPrice.currency==self.currency.data)).first()
            if not exists == None:
                raise ValidationError(_l('Price value already exists')+'. '+_l('Please consider activating the existing one')+'.')
