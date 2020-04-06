from datetime import date, timedelta
from flask_login import UserMixin
from elibrary import db, login_manager
from elibrary.utils.numeric_defines import MEMBERSHIP_EXTENSION_DAYS, EXPIRATION_EXTENSION_LIMIT

@login_manager.user_loader
def load_user(user_id):
    return Librarian.query.get(int(user_id))

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(10), nullable=False, unique=True)   #TODO customize after consultation, auto increment if integer!
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(40), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(120), nullable=True)
    phone_1 = db.Column(db.String(15), nullable=False)
    phone_2 = db.Column(db.String(15), nullable=True)
    address = db.Column(db.String(50), nullable=False)
    town = db.Column(db.String(20), nullable=False)
    date_registered = db.Column(db.Date, nullable=False, default=date.today())
    date_expiration = db.Column(db.Date, nullable=False, default=date.today() + timedelta(MEMBERSHIP_EXTENSION_DAYS))
    total_books_rented = db.Column(db.Integer, nullable=False, default=0)
    #TODO lista knjiga koje su trenutno kod njega

    @property
    def phone_1_formated(self):
        if "+" in self.phone_1:
            return self.phone_1
        else:
            return self.phone_1[:3] + '/' + self.phone_1[3:]

    @property
    def phone_2_formated(self):
        if not (self.phone_2 == "" or self.phone_2 == None):
            if "+" in self.phone_2:
                return self.phone_2
            else:
                return self.phone_2[:3] + '/' + self.phone_2[3:]
        else:
            return ""

    @property
    def is_membership_expired(self):
        return self.date_expiration < date.today()

    @property
    def is_membership_near_expired(self):
        return self.date_expiration <= date.today() + timedelta(EXPIRATION_EXTENSION_LIMIT) and self.date_expiration >= date.today()

    @property
    def age(self):
        today = date.today()
        return int(today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day)))

    @property
    def has_rented_books(self):
        return true

    def __repr__(self):
#        return f"Member('{self.first_name}', '{self.last_name}', '{self.date_expiration}')" #dodati i broj knjiga
        return f"Member('{self.id}', '{self.first_name}', '{self.last_name}', '{self.birth_date}',\
                      '{self.email}', '{self.mobile_phone}', '{self.home_phone}', '{self.address}',\
                      '{self.town}', '{self.date_registered}', '{self.date_expiration}')"

class Librarian(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(40), nullable=False)
    username = db.Column(db.String(30), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    email = db.Column(db.String(120), nullable=True)
    phone_1 = db.Column(db.String(15), nullable=False)
    phone_2 = db.Column(db.String(15), nullable=True)
    address = db.Column(db.String(50), nullable=False)
    town = db.Column(db.String(20), nullable=False)
    date_registered = db.Column(db.Date, nullable=False, default=date.today())
    is_admin = db.Column(db.Boolean, default=False)
    is_operational = db.Column(db.Boolean, default=True)
    change_password = db.Column(db.Boolean, default=False)
    change_username_value = db.Column(db.String(30), nullable=True)
    change_username = db.Column(db.Boolean, default=False)

    @property
    def phone_1_formated(self):
        if "+" in self.phone_1:
            return self.phone_1
        else:
            return self.phone_1[:3] + '/' + self.phone_1[3:]

    @property
    def phone_2_formated(self):
        if not (self.phone_2 == "" or self.phone_2 == None):
            if "+" in self.phone_2:
                return self.phone_2
            else:
                return self.phone_2[:3] + '/' + self.phone_2[3:]
        else:
            return ""

    def __repr__(self):
#        return f"User('{self.username}', '{self.is_active}', '{self.is_admin}')"
        return f"User('{self.id}', '{self.first_name}', '{self.last_name}', '{self.username}',\
                      '{self.password}', '{self.email}', '{self.mobile_phone}',\
                      '{self.home_phone}', '{self.address}', '{self.town}',\
                      '{self.date_registered}', '{self.is_admin}', '{self.is_operational}')"
