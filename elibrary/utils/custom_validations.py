from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp, optional
from flask_babel import lazy_gettext as _l

class required_cust(DataRequired):
    def __init__(self, text = _l('The field must be filled')+'.'):
        DataRequired.__init__(self, message = text)

class optional_cust(optional):
    def __init__(self):
        optional.__init__(self)

class email_cust(Email):
    def __init__(self, text = _l('Value does not match e-mail format')+'.'):
        Email.__init__(self, message = text)

class phone_cust(Regexp):
    def __init__(self, text = _l('Phone number does not match expected format')+'. '+\
                _l('E.g. 063/1128767, +381631128767, +381 63 1128767, 025/343565, +38125343565, +381 25 343565')+'.'):
        Regexp.__init__(self, '^((\+\d{1,3} \d{2} )|(\+\d{1,3}\d{2})|(0\d{2}\/))\d{6,8}$', message = text)

class string_cust(Regexp):
    def __init__(self, text = _l('Only letters, numbers, spaces and hyphens are allowed')+'.'):
        Regexp.__init__(self, '^[\w\- ]*$', message = text)

class username_cust(Regexp):
    def __init__(self, text = _l('Only letters, numbers, and following characters are allowed')+': - ! " # % & \' ( ) * + / \\ . ? @'):
        Regexp.__init__(self, '^[\w\-\!\"\#\%\&\'\(\)\*\+\/\\\.\?\@]*$', message = text)

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
