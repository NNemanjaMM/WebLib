import enum
from datetime import date, timedelta
from flask_login import UserMixin
from elibrary import db, login_manager
from elibrary.utils.defines import EXPIRATION_EXTENSION_LIMIT, DATE_FORMAT, DATETIME_FORMAT, DATETIME_ALL_FORMAT, BOOK_RENT_PERIOD
from flask_babel import gettext, lazy_gettext as _l

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

    def log_data(self):
        if not (self.inv_number and self.signature and self.title and self.author):
            return '<br/>'+_l('More data is currently unavailable')
        return '<br/>'+_l('Inventory number')+': '+str(self.inv_number)+\
                '<br/>'+_l('Signature')+': '+self.signature+\
                '<br/>'+_l('Title')+': '+self.title+\
                '<br/>'+_l('Author')+': '+self.author

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

    def log_data(self):
        if not (self.first_name and self.father_name and self.last_name and self.profession and self.phone and self.address and self.email):
            return '<br/>'+_l('More data is currently unavailable')
        return '<br/>'+_l('First name')+': '+self.first_name+\
                '<br/>'+_l('Father name')+': '+self.father_name+\
                '<br/>'+_l('Last name')+': '+self.last_name+\
                '<br/>'+_l('Profession')+': '+self.profession+\
                '<br/>'+_l('Phone')+': '+self.phone+\
                '<br/>'+_l('Address')+': '+self.address+\
                '<br/>'+_l('E-mail address')+': '+self.email

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
    email = db.Column(db.String(40), nullable=True)
    phone = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(50), nullable=False)
    date_registered = db.Column(db.Date, nullable=False, default=date.today())
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    change_admin = db.Column(db.Boolean, default=False)
    change_password = db.Column(db.Boolean, default=False)
    user_key = db.Column(db.String(160), nullable=True)

    def log_data(self):
        if not (self.first_name and self.last_name and self.phone and self.address and self.email):
            return '<br/>'+_l('More data is currently unavailable')
        return '<br/>'+_l('First name')+': '+self.first_name+\
                '<br/>'+_l('Last name')+': '+self.last_name+\
                '<br/>'+_l('Phone')+': '+self.phone+\
                '<br/>'+_l('Address')+': '+self.address+\
                '<br/>'+_l('E-mail address')+': '+self.email

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

    def log_data(self):
        return '<br/>'+_l('Price')+': '+self.price_value_print+' '+self.currency+\
                '<br/>'+_l('Note')+': '+self.note

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

    @property
    def price_and_currency_print(self):
        return "{:.2f}".format(self.price) + " " + self.price_details.currency

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
            return _l('Yes')
        else:
            return _l('No')

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
   librarian_remove_admin_request = 58  #
   librarian_remove_admin_response = 59 #

   type_text = {
       0: _l('Not selected'),
       book_add: _l('Book add'),
       book_update: _l('Book update'),
       book_error_add: _l('Book error add'),
       book_error_remove: _l('Book error remove'),
       rent_rent: _l('Book rent'),
       rent_return: _l('Book return'),
       member_add: _l('Member add'),
       member_update: _l('Member update'),
       extension_add: _l('Membership extension'),
       price_add: _l('Price add'),
       price_enabled: _l('Price activation'),
       price_disabled: _l('Price deactivation'),
       librarian_add: _l('Librarian add'),
       librarian_update: _l('Librarian update'),
       librarian_password: _l('Librarian password change'),
       librarian_password_request: _l('Librarian password change request'),
       librarian_password_response: _l('Librarian password change response'),
       librarian_activate: _l('Librarian activation'),
       librarian_deactivate: _l('Librarian deactivation'),
       librarian_set_admin: _l('Librarian set as admin'),
       librarian_remove_admin_request: _l('Librarian remove admin request'),
       librarian_remove_admin_response: _l('Librarian remove admin response'),
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
    message = db.Column(db.String(450), nullable=False)
    is_seen = db.Column(db.Boolean, default=False)

    @property
    def type_print(self):
        return EventType.get_type_text(self.type)

    @property
    def time_print(self):
        return self.time.strftime(DATETIME_FORMAT)

    @property
    def time_all_print(self):
        return self.time.strftime(DATETIME_ALL_FORMAT)

    @property
    def object_id_print(self):
        if(self.type < 20):
            return _l('Book with id') + ' ' + str(self.object_id)
        elif(self.type < 40):
            return _l('Member with id') + ' ' + str(self.object_id)
        elif(self.type < 50):
            return _l('Price with id') + ' ' + str(self.object_id)
        elif(self.type < 60):
            return _l('Librarian with id') + ' ' + str(self.object_id)
        else:
            return ''
