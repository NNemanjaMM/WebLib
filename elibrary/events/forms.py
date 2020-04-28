from flask_wtf import FlaskForm
from flask_babel import gettext, lazy_gettext as _l
from wtforms import StringField, SubmitField, SelectField
from elibrary.models import EventType

class FilterForm(FlaskForm):
    date_from = StringField(_l('Event date after'))
    date_to = StringField(_l('Event date before'))
    librarian = StringField(_l('Librarian'))
    type = SelectField(_l('Event type'), choices=list(EventType.type_text.items()))
    object_id = StringField(_l('Object id'))
    submit = SubmitField(_l('Filter'))
