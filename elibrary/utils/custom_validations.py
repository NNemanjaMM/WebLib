from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, optional
from flask_babel import gettext as _g
from datetime import datetime, date
from elibrary.utils.defines import MINIMUM_DATE, MAXIMUM_NUMBER, DATE_FORMAT

class required_cust(DataRequired):
    def __init__(self, text = _g('Field can not be empty')+'.'):
        DataRequired.__init__(self, message = text)

class required_cust_date(DataRequired):
    def __init__(self, text = _g('Value is not a valid date') + '. ' + _g('Make sure it matches the following format') + ' ' + _g('"dd.mm.yyyy."') + '.'):
        DataRequired.__init__(self, message = text)

class required_cust_decimal(DataRequired):
    def __init__(self, text = _g('Value is not a valid decimal number') + '. ' + _g('Make sure it uses dot as decimal point') + '.'):
        DataRequired.__init__(self, message = text)

class optional_cust(optional):
    def __init__(self):
        optional.__init__(self)

class email_cust(Email):
    def __init__(self, text = _g('Value does not match e-mail address format')+'.'):
        Email.__init__(self, message = text)

class phone_cust(Regexp):
    def __init__(self, text = _g('Value does not match expected phone number format')+'. '+\
                _g('E.g. 069/1128767, 0691128767, +387691128767, 059/343565, 059343565, +38759343565')+'.'):
        Regexp.__init__(self, '^((0\d{2}\/)|(0\d{2})|(\+\d{1,3}\d{2}))\d{6,8}$', message = text)

class string_cust(Regexp):
    def __init__(self, text = _g('Only letters, numbers, spaces, dots, commas, and hyphens are allowed')+'.'):
        Regexp.__init__(self, '^[\w\-\.\, ]*$', message = text)

class char_cust(Regexp):
    def __init__(self, text = _g('Only upper case letters are allowed')+'.'):
        Regexp.__init__(self, '^[A-Z]*$', message = text)

class username_cust(Regexp):
    def __init__(self, text = _g('Only letters, numbers, and following characters are allowed')+': - ! " # % & \' ( ) * + / \\ . ? @'):
        Regexp.__init__(self, '^[\w\-\!\"\#\%\&\'\(\)\*\+\/\\\.\?\@]*$', message = text)

class signature_cust(Regexp):
    def __init__(self, text = _g('Only numbers, dots, and hyphens are allowed')+'.'):
        Regexp.__init__(self, '^[\d\.\-]*$', message = text)

class numeric_cust(Regexp):
    def __init__(self, text = _g('Only digits are allowed')+'.'):
        Regexp.__init__(self, '^[\d]*$', message = text)

class equal_to_cust(EqualTo):
    def __init__(self, field, text = _g('Confirm password')+' '+_g('does not match the')+' '+_g('Password')+'.'):
        EqualTo.__init__(self, field, message = text)

class length_cust(Length):
    def __init__(self, min = -1, max = -1):
        if not (min == -1 or max == -1):
            text = _g('Input length must be between') + ' ' + str(min) + ' ' + 'and' + ' ' + str(max) + ' ' + _g('characters') + '.'
        elif not max == -1:
            text = _g('Maximum input length is') + ' ' + str(max) + ' ' + _g('characters') + '.'
        else:
            text = _g('Minimum input length is') + ' ' + str(min) + ' ' + _g('characters') +'.'
        Length.__init__(self, min, max, message = text)

class length_cust_max(Length):
    def __init__(self, max = 50):
        text = _g('Maximum input length is') + ' ' + str(max) + ' ' + _g('characters') + '.'
        Length.__init__(self, -1, max, message = text)

class length_cust_max_15(length_cust_max):
    def __init__(self, maximum=15):
        length_cust_max.__init__(self, max = maximum)

class FieldValidator():
    @staticmethod
    def validate_field(form, field, validator_classes):
        field.errors = list()
        for validator_class in validator_classes:
            validator = validator_class()
            try:
                validator(form, field)
            except ValueError as e:
                field.errors.append(e.args[0])
        return len(field.errors) == 0

    @staticmethod
    def validate_required_field(form, field, validator_classes):
        field.errors = list()
        if not field.data:
            field.errors.append(_g('Field can not be empty')+'.')
        else:
            for validator_class in validator_classes:
                validator = validator_class()
                try:
                    validator(form, field)
                except ValueError as e:
                    field.errors.append(e.args[0])
        return len(field.errors) == 0

    @staticmethod
    def convert_and_validate_date(field, allow_future, date_min_str = MINIMUM_DATE):
        value = None
        field.errors = list()
        try:
            value = datetime.strptime(field.data, "%d.%m.%Y.").date()
        except ValueError:
            field.errors.append(_g('Value is not a valid date') + '. ' + _g('Make sure it matches the following format') + ' ' + _g('"dd.mm.yyyy."') + '.')
        if not value == None:
            if value < datetime.strptime(date_min_str, "%d.%m.%Y.").date():
                field.errors.append(_g('Date can not be set before') + ' "' + str(date_min_str) + '".')
                value = None
            elif not allow_future and value > date.today():
                field.errors.append(_g('Date can not be set in future') + '.')
                value = None
        return value

    @staticmethod
    def validate_date_order(first_date_value, second_date_value, second_date_field):
        second_date_field.errors = list()
        if not first_date_value <= second_date_value:
            second_date_field.errors.append(_g('"After" date value can not be set after the "before" date value') + '.')
        return len(second_date_field.errors) == 0

    @staticmethod
    def convert_and_validate_number(field):
        value = None
        field.errors = list()
        try:
            value = int(field.data)
        except ValueError:
            field.errors.append(_g('Value is not a valid whole number') + '.')
        if not value == None:
            if value < 0:
                field.errors.append(_g('Number can not be lower than zero') + '.')
                value = None
            elif value > MAXIMUM_NUMBER:
                field.errors.append(_g('Number can not be higher than') + ' ' + str(MAXIMUM_NUMBER) + '.')
                value = None
        return value

    @staticmethod
    def validate_number_order(first_number_value, second_number_value, second_number_field):
        second_number_field.errors = list()
        if not first_number_value <= second_number_value:
            second_number_field.errors.append(_g('"Higher than" value can not be greater than "lower than" value') + '.')
        return len(second_number_field.errors) == 0
