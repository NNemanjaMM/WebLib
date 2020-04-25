from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, optional
from flask_babel import lazy_gettext as _l
from datetime import datetime, date
from elibrary.utils.defines import MINIMUM_DATE, MAXIMUM_NUMBER, DATE_FORMAT

class required_cust(DataRequired):
    def __init__(self, text = _l('The field must be filled')+'.'):
        DataRequired.__init__(self, message = text)

class required_cust_date(DataRequired):
    def __init__(self, text = _l('Date value is not valid') + '. ' + _l('Make sute if matches the following format') + ' ' + _l('"dd.mm.yyyy."') + '.'):
        DataRequired.__init__(self, message = text)

class required_cust_decimal(DataRequired):
    def __init__(self, text = _l('Decimal value is not valid') + '. ' + _l('Make sure it is a decimal number and uses dot as decimal point') + '.'):
        DataRequired.__init__(self, message = text)

class optional_cust(optional):
    def __init__(self):
        optional.__init__(self)

class email_cust(Email):
    def __init__(self, text = _l('Value does not match e-mail format')+'.'):
        Email.__init__(self, message = text)

class phone_cust(Regexp):
    def __init__(self, text = _l('Phone number does not match expected format')+'. '+\
                _l('E.g. 069/1128767, 0691128767, +387691128767, 059/343565, 059343565, +38759343565')+'.'):
        Regexp.__init__(self, '^((0\d{2}\/)|(0\d{2})|(\+\d{1,3}\d{2}))\d{6,8}$', message = text)

class string_cust(Regexp):
    def __init__(self, text = _l('Only letters, numbers, spaces, dots, commas, and hyphens are allowed')+'.'):
        Regexp.__init__(self, '^[\w\-\.\, ]*$', message = text)

class char_cust(Regexp):
    def __init__(self, text = _l('Only upper case letters are allowed')+'.'):
        Regexp.__init__(self, '^[A-Z]*$', message = text)

class username_cust(Regexp):
    def __init__(self, text = _l('Only letters, numbers, and following characters are allowed')+': - ! " # % & \' ( ) * + / \\ . ? @'):
        Regexp.__init__(self, '^[\w\-\!\"\#\%\&\'\(\)\*\+\/\\\.\?\@]*$', message = text)

class signature_cust(Regexp):
    def __init__(self, text = _l('Only numbers, dots, and hyphens are allowed')+'.'):
        Regexp.__init__(self, '^[\d\.\-]*$', message = text)

class numeric_cust(Regexp):
    def __init__(self, text = _l('Only digits are allowed')+'.'):
        Regexp.__init__(self, '^[\d]*$', message = text)

class equal_to_cust(EqualTo):
    def __init__(self, field, text = _l('Confirm password')+' '+_l('does not match the')+' '+_l('Password')+'.'):
        EqualTo.__init__(self, field, message = text)

class length_cust(Length):
    def __init__(self, min = -1, max = -1):
        if not (min == -1 or max == -1):
            text = _l('Input length must be between') + ' ' + str(min) + ' ' + 'and' + ' ' + str(max) + ' ' + _l('characters') + '.'
        elif not max == -1:
            text = _l('Maximum input length must be') + ' ' + str(max) + ' ' + _l('characters') + '.'
        else:
            text = _l('Minimum input length must be') + ' ' + str(min) + ' ' + _l('characters') +'.'
        Length.__init__(self, min, max, message = text)

class length_cust_max(Length):
    def __init__(self, max = 50):
        text = _l('Input length can not be greather than') + ' ' + str(max) + ' ' + _l('characters') + '.'
        Length.__init__(self, -1, max, message = text)

class length_cust_max_15(length_cust_max):
    def __init__(self, maximum=15):
        length_cust_max.__init__(self, max = maximum)

class required_cust_2():
     def __call__(self, form, field):
        try:
            if field.data is None:
                raise email_validator.EmailNotValidError()
            email_validator.validate_email(
                field.data,
                check_deliverability=self.check_deliverability,
                allow_smtputf8=self.allow_smtputf8,
                allow_empty_local=self.allow_empty_local,
            )
        except email_validator.EmailNotValidError as e:
            message = self.message
            if message is None:
                if self.granular_message:
                    message = field.gettext(e)
                else:
                    message = field.gettext("Invalid email address.")
            raise ValidationError(message)

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
            field.errors.append(_l('Field can not be empty')+'.')
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
            field.errors.append(_l('Date value is not valid') + '. ' + _l('Make sute if matches the following format') + ' ' + _l('"dd.mm.yyyy."') + '.')
        if not value == None:
            if value < datetime.strptime(date_min_str, "%d.%m.%Y.").date():
                field.errors.append(_l('Date can not be set before') + ' "' + str(date_min_str) + '".')
                value = None
            elif not allow_future and value > date.today():
                field.errors.append(_l('Date can not be set in future') + '.')
                value = None
        return value

    @staticmethod
    def validate_date_order(first_date_value, second_date_value, second_date_field):
        second_date_field.errors = list()
        if not first_date_value <= second_date_value:
            second_date_field.errors.append(_l('Before date value can not be set after the after date value') + '.')
        return len(second_date_field.errors) == 0

    @staticmethod
    def convert_and_validate_number(field):
        value = None
        field.errors = list()
        try:
            value = int(field.data)
        except ValueError:
            field.errors.append(_l('Value is not a valid whole number') + '.')
        if not value == None:
            if value < 0:
                field.errors.append(_l('Number can not be lower than zero') + '.')
                value = None
            elif value > MAXIMUM_NUMBER:
                field.errors.append(_l('Number can not be greater than') + ' ' + str(MAXIMUM_NUMBER) + '.')
                value = None
        return value

    @staticmethod
    def validate_number_order(first_number_value, second_number_value, second_number_field):
        second_number_field.errors = list()
        if not first_number_value <= second_number_value:
            second_number_field.errors.append(_l('Greater than value can not be higher than lower than value') + '.')
        return len(second_number_field.errors) == 0
