from datetime import date, timedelta
from flask_login import UserMixin
from elibrary import db, login_manager
from elibrary.utils.numeric_defines import MEMBERSHIP_EXTENSION_DAYS, EXPIRATION_EXTENSION_LIMIT

@login_manager.user_loader
def load_user(user_id):
    return Librarian.query.get(int(user_id))

class Book(db.Model):     #za knjigu signatura (10 cifara, ima i tacke i povlake), inventarni broj (broj, 50000), naslov, autor
    id = db.Column(db.Integer, primary_key=True)
    signature = db.Column(db.String(16), nullable=False)
    inv_number = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String(60), nullable=False)
    author = db.Column(db.String(70), nullable=False)

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
    date_expiration = db.Column(db.Date, nullable=True)
    total_books_rented = db.Column(db.Integer, nullable=False, default=0)
    membership_extensions = db.relationship("Extension", backref='member', lazy=True)

    @property
    def phone_formated(self):
        if "+" in self.phone:
            return self.phone
        else:
            return self.phone[:3] + '/' + self.phone[3:]

    @property
    def is_membership_expired(self):
        return self.date_expiration < date.today()

    @property
    def is_membership_near_expired(self):
        return self.date_expiration <= date.today() + timedelta(EXPIRATION_EXTENSION_LIMIT) and self.date_expiration >= date.today()

    @property
    def number_of_rented_books(self):
        return 0#len(self.rented_books)

    def __repr__(self):
        return f"Member('{self.id}', '{self.first_name}', '{self.last_name}', '{self.father_name}', \
                      '{self.profession}', '{self.email}', '{self.phone_formated}', '{self.address}',\
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
    is_operational = db.Column(db.Boolean, default=True)
    change_password = db.Column(db.Boolean, default=False)
    change_username_value = db.Column(db.String(30), nullable=True)
    memberships_extended = db.relationship("Extension", backref='librarian', lazy=True)

    @property
    def change_username(self):
        return not self.change_username_value == None

    @property
    def phone_formated(self):
        if "+" in self.phone:
            return self.phone
        else:
            return self.phone[:3] + '/' + self.phone[3:]

    def __repr__(self):
        return f"User('{self.id}', '{self.first_name}', '{self.last_name}', '{self.username}', '{self.email}', \
                      '{self.phone_formated}', '{self.address}', '{self.date_registered}', '{self.is_admin}', \
                      '{self.is_operational}', '{self.change_password}', '{self.change_username}')"

class Extension(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    is_paid = db.Column(db.Boolean, default=False)
    price = db.Column(db.Integer, nullable=True)
    date_performed = db.Column(db.Date, nullable=False, default=date.today())
    date_extended = db.Column(db.Date, nullable=False, default=date.today())
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    librarian_id = db.Column(db.Integer, db.ForeignKey('librarian.id'), nullable=False)

class Rental(db.Model): # povezati sa knjigom, clanom, ko je odobrio, i ko je preuzeo knjigu nazad
    id = db.Column(db.Integer, primary_key=True)
    date_performed = db.Column(db.Date, nullable=False, default=date.today())
    date_termination = db.Column(db.Date, nullable=False, default=date.today() + timedelta(EXPIRATION_EXTENSION_LIMIT))
    is_terminated = db.Column(db.Boolean, default=False)
