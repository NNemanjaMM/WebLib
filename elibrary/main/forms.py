from flask_wtf import FlaskForm
from flask_babel import lazy_gettext as _l
from wtforms import StringField, PasswordField, SubmitField, SelectField, IntegerField, TextAreaField
from wtforms.validators import DataRequired, Length, Email, EqualTo, optional

class BookForm(FlaskForm):  # Proveriti koja polja su potrebna za knjigu
    title = StringField(_l('Title'), validators=[DataRequired(), Length(max=40)])
    author = StringField(_l('Author'), validators=[DataRequired(), Length(max=40)])
    label = StringField(_l('Label'), validators=[DataRequired(), Length(max=40)])
    genre = SelectField(_l('Genre'), choices=[])
    # genre.choices = [(genre.id, genre.name) for genre in Genre.query.all()]
    original_title = StringField(_l('Original title'), validators=[DataRequired(), Length(max=60)])
    pages = IntegerField(_l('Number of pages'), validators=[optional()])
    year = IntegerField(_l('Publication year'), validators=[optional()])
    tags = TextAreaField(_l('Tags'), validators=[optional()])
    publisher = StringField(_l('Publisher'), validators=[optional(), Length(max=50)])

class CreateBookForm(BookForm):
    submit = SubmitField(_l('Add book'))

class UpdateBookForm(BookForm):
    submit = SubmitField(_l('Update book'))


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
