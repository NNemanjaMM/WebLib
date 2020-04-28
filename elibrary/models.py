import enum
from datetime import date, timedelta
from flask_login import UserMixin
from elibrary import db, login_manager
from elibrary.utils.defines import EXPIRATION_EXTENSION_LIMIT, DATE_FORMAT, DATETIME_FORMAT, BOOK_RENT_PERIOD
from flask_babel import gettext

@login_manager.user_loader
def load_user(user_id):
    return Librarian.query.get(int(user_id))

class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    inv_number = db.Column(db.Integer, nullable=False)
    signature = db.Column(db.String(16), nullable=False)
    title = db.Column(db.String(60), nullable=False)
    author = db.Column(db.String(70), nullable=False)
    is_rented = db.Column(db.Boolean, default=False)
    has_error = db.Column(db.Boolean, default=False)

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    father_name = db.Column(db.String(20), nullable=False)
    profession = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(60), nullable=False)
    date_registered = db.Column(db.Date, nullable=False, default=date.today())
    date_expiration = db.Column(db.Date, nullable=True, default=date.today())
    total_books_rented = db.Column(db.Integer, nullable=False, default=0)
    number_of_rented_books = db.Column(db.Integer, nullable=False, default=0)

    @property
    def is_membership_expired(self):
        return self.date_expiration < date.today()

    @property
    def is_membership_near_expired(self):
        return self.date_expiration <= date.today() + timedelta(EXPIRATION_EXTENSION_LIMIT) and self.date_expiration >= date.today()

    @property
    def phone_print(self):
        if "+" in self.phone:
            return self.phone
        else:
            return self.phone[:3] + '/' + self.phone[3:]
    @property
    def date_registered_print(self):
        return self.date_registered.strftime(DATE_FORMAT)

    @property
    def date_expiration_print(self):
        return self.date_expiration.strftime(DATE_FORMAT)

    def __repr__(self):
        return f"Member('{self.id}', '{self.first_name}', '{self.last_name}', '{self.father_name}', \
                      '{self.profession}', '{self.email}', '{self.phone_print}', '{self.address}',\
                      '{self.total_books_rented}', '{self.date_registered}', '{self.date_expiration}')"

class Librarian(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    username = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(50), nullable=True)
    phone = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(60), nullable=False)
    date_registered = db.Column(db.Date, nullable=False, default=date.today())
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    change_admin = db.Column(db.Boolean, default=False)
    change_password = db.Column(db.Boolean, default=False)

    @property
    def phone_print(self):
        if "+" in self.phone:
            return self.phone
        else:
            return self.phone[:3] + '/' + self.phone[3:]

    @property
    def date_registered_print(self):
        return self.date_registered.strftime(DATE_FORMAT)

    def __repr__(self):
        return f"User('{self.id}', '{self.first_name}', '{self.last_name}', '{self.username}', '{self.email}', \
                      '{self.phone_print}', '{self.address}', '{self.date_registered}', '{self.is_admin}', \
                      '{self.is_active}', '{self.change_password}')"

class ExtensionPrice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    price_value = db.Column(db.Numeric(scale=2, precision=4, asdecimal=True), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    note = db.Column(db.String(150), nullable=True)
    is_enabled = db.Column(db.Boolean, nullable=False, default=True)

    @property
    def price_value_print(self):
        return "{:.2f}".format(self.price_value)

    def __repr__(self):
        return "{:.2f}".format(self.price_value) + ' ' + self.currency

class Extension(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    note = db.Column(db.String(150), nullable=True)
    price = db.Column(db.Numeric, nullable=False)
    date_performed = db.Column(db.Date, nullable=False, default=date.today())
    date_extended = db.Column(db.Date, nullable=False, default=date.today())
    price_id = db.Column(db.Integer, db.ForeignKey(ExtensionPrice.id), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey(Member.id), nullable=False)
    price_details = db.relationship('ExtensionPrice', foreign_keys=[price_id])
    member = db.relationship('Member', foreign_keys=[member_id])

    @property
    def date_performed_print(self):
        return self.date_performed.strftime(DATE_FORMAT)

    @property
    def date_extended_print(self):
        return self.date_extended.strftime(DATE_FORMAT)

    @property
    def price_print(self):
        return "{:.2f}".format(self.price)

class Rental(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date_performed = db.Column(db.Date, nullable=False, default=date.today())
    date_deadline = db.Column(db.Date, nullable=False, default=date.today() + timedelta(BOOK_RENT_PERIOD))
    date_termination = db.Column(db.Date, nullable=True)
    is_terminated = db.Column(db.Boolean, default=False)
    book_id = db.Column(db.Integer, db.ForeignKey(Book.id), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey(Member.id), nullable=False)
    book = db.relationship("Book", foreign_keys=[book_id])
    member = db.relationship("Member", foreign_keys=[member_id])

    @property
    def date_deadline_passed(self):
        if self.is_terminated:
            return True if self.date_deadline < self.date_termination else False
        else:
            return True if self.date_deadline < date.today() else False

    @property
    def returned_deadline_passed(self):
        if self.is_terminated:
            return True if self.date_termination > self.date_deadline else False
        return False

    @property
    def date_performed_print(self):
        return self.date_performed.strftime(DATE_FORMAT)

    @property
    def date_termination_print(self):
        return self.date_termination.strftime(DATE_FORMAT)

    @property
    def date_deadline_print(self):
        return self.date_deadline.strftime(DATE_FORMAT)

    @property
    def is_terminated_print(self):
        if self.is_terminated:
            return gettext('Yes')
        else:
            return gettext('No')

class EventType():
   book_add = 1
   book_update = 2
   book_error_add = 3
   book_error_remove = 4
   rent_rent = 11
   rent_return = 12
   member_add = 21
   member_update = 22
   extension_add = 31
   price_add = 41
   price_enabled = 42
   price_disabled = 43
   librarian_add = 50
   librarian_update = 51
   librarian_password = 52
   librarian_password_request = 53
   librarian_password_response = 54
   librarian_activate = 55
   librarian_deactivate = 56
   librarian_set_admin = 57
   librarian_remove_admin_request = 58
   librarian_remove_admin_response = 59

   type_text = {
       book_add: gettext('Book add'),
       book_update: gettext('Book update'),
       book_error_add: gettext('Book error add'),
       book_error_remove: gettext('Book error remove'),
       rent_rent: gettext('Book rent'),
       rent_return: gettext('Book return'),
       member_add: gettext('Member add'),
       member_update: gettext('Member update'),
       extension_add: gettext('Membership extension'),
       price_add: gettext('Price add'),
       price_enabled: gettext('Price activation'),
       price_disabled: gettext('Price deactivation'),
       librarian_add: gettext('Librarian add'),
       librarian_update: gettext('Librarian update'),
       librarian_password: gettext('Librarian password change'),
       librarian_password_request: gettext('Librarian password change request'),
       librarian_password_response: gettext('Librarian password change response'),
       librarian_activate: gettext('Librarian activation'),
       librarian_deactivate: gettext('Librarian deactivation'),
       librarian_set_admin: gettext('Librarian set as admin'),
       librarian_remove_admin_request: gettext('Librarian remove admin request'),
       librarian_remove_admin_response: gettext('Librarian remove admin response'),
   };

   @staticmethod
   def get_type_text(id):
       return EventType.type_text[id]

class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime, nullable=True)
    librarian = db.Column(db.String(30), nullable=False)
    type = db.Column(db.Integer, nullable=False)
    object_id = db.Column(db.Integer, nullable=True)
    message = db.Column(db.String(300), nullable=False)

    @property
    def type_print(self):
        return EventType.get_type_text(self.type)

    @property
    def time_print(self):
        return self.time.strftime(DATETIME_FORMAT)

    @property
    def object_id_print(self):
        if(self.type < 20):
            return gettext('Book with id') + ' ' + str(self.object_id)
        elif(self.type < 40):
            return gettext('Member with id') + ' ' + str(self.object_id)
        elif(self.type < 50):
            return gettext('Price with id') + ' ' + str(self.object_id)
        elif(self.type < 60):
            return ''
