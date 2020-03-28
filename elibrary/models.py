from elibrary import db, login_manager
from flask_login import UserMixin
from datetime import date, timedelta

@login_manager.user_loader
def load_user(user_id):
    return Librarian.query.get(int(user_id))

class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(20), nullable=False)
    last_name = db.Column(db.String(40), nullable=False)
    birth_year = db.Column(db.Integer, nullable=False)
    email = db.Column(db.String(120), nullable=True)
    phone_1 = db.Column(db.String(15), nullable=False)
    phone_2 = db.Column(db.String(15), nullable=True)
    address = db.Column(db.String(50), nullable=False)
    town = db.Column(db.String(20), nullable=False)
    date_registered = db.Column(db.Date, nullable=False, default=date.today())
    date_expiration = db.Column(db.Date, nullable=False, default=date.today() + timedelta(days=365))
    books_rented = db.Column(db.Integer, nullable=False, default=0)
    #TODO lista knjiga koje su trenutno kod njega

    def __repr__(self):
#        return f"Member('{self.first_name}', '{self.last_name}', '{self.date_expiration}')" #dodati i broj knjiga
        return f"Member('{self.id}', '{self.first_name}', '{self.last_name}', '{self.birth_year}',\
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

    def __repr__(self):
#        return f"User('{self.username}', '{self.is_active}', '{self.is_admin}')"
        return f"User('{self.id}', '{self.first_name}', '{self.last_name}', '{self.username}',\
                      '{self.password}', '{self.email}', '{self.mobile_phone}',\
                      '{self.home_phone}', '{self.address}', '{self.town}',\
                      '{self.date_registered}', '{self.is_admin}', '{self.is_operational}')"
