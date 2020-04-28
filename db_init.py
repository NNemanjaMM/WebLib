from datetime import date, datetime, timedelta
from elibrary.models import Librarian, Member, ExtensionPrice, Book, Extension, Rental, Event, EventType
from elibrary import db, create_app, bcrypt

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    pass1 = bcrypt.generate_password_hash('mikamika').decode('utf-8')
    pass2 = bcrypt.generate_password_hash('perapera').decode('utf-8')
    pass3 = bcrypt.generate_password_hash('djokadjoka').decode('utf-8')
    admin2 = Librarian(first_name='Pera', last_name='Perić', username='pera.peric', password=pass2, phone='0651128767', address='Peroslava Perića 5, Bileća', is_admin=True, date_registered=date(1991, 7, 23))
    admin1 = Librarian(first_name='Mika', last_name='Mikić', username='mika.mikic', password=pass1, email='mikam@gmail.com', phone='+387664408404', address='Milivoja Mikića 3, Nevesinje', date_registered=date(2013, 9, 3))
    admin3 = Librarian(first_name='Đoka', last_name='Đokić', username='djoka.djokic', password=pass3, email='djoka.kralj@outlook.com', phone='0591128767', address='Đorđija Đokića 21, Istočno Sarajevo', date_registered=date(2002, 11, 14), is_active=False)
        
    db.session.add(admin1)
    db.session.add(admin2)
    db.session.add(admin3)

    member1 = Member(id=3, first_name='Steva', last_name='Zikic', father_name='Jovan', profession='dip. Ekonomista', phone='+38763898554', email='steva.zikic22@live.com', address='Zike Zikica 21, Pirot', date_registered=date(2016, 2, 18), total_books_rented=15, date_expiration=date(2021, 2, 24), number_of_rented_books=1)
    member2 = Member(id=18, first_name='Vida', last_name='Stevic', father_name='Petar', profession='dip. Pravnik', phone='0594545332', address='Stevice Stevovica 54, Beograd', date_registered=date(2011, 5, 12), total_books_rented=1, date_expiration=date(2012, 5, 12), number_of_rented_books=1)
    member3 = Member(id=24, first_name='Rade', last_name='Vidic', father_name='Luka', profession='dip. inž. Mašinstva', phone='0654433565', email='radev@gmail.com', address='Vidvdanska 8, Valjevo', date_registered=date(1998, 3, 18), total_books_rented=16754, date_expiration=date(2020, 5, 20), number_of_rented_books=1)
    member4 = Member(id=42, first_name='Ana', last_name='Radovic', father_name='Matej', profession='master Biologije', phone='066232445', address='Bulevar Radoslava Radenkovića Raše 133, Kosovska Mitrovica', date_registered=date(2008, 10, 27), total_books_rented=375, date_expiration=date(2019, 10, 7), number_of_rented_books=0)
    member5 = Member(id=76, first_name='Žika', last_name='Anic', father_name='Andrej', profession='dr Primenjene Matematike', phone='+387593037566', email='zikans@gmail.com', address='Atinska 58, Novi Sad', date_registered=date(2019, 7, 23), total_books_rented=2742, date_expiration=date(2020, 7, 23), number_of_rented_books=2)
    member6 = Member(id=103, first_name='Petar', last_name='Milov', father_name='Nikola', profession='dipl. Fizičar', phone='+387691215464', address='Fruškogorska 12, Sremska Kamenica', date_registered=date(2012, 8, 14), total_books_rented=12, date_expiration=date(2020, 12, 30), number_of_rented_books=4)
    member7 = Member(id=104, first_name='Vera', last_name='Milov', father_name='Nikola', profession='dipl. Hemičar', phone='+387695545465', address='Fruškogorska 12, Sremska Kamenica', date_registered=date(2012, 8, 14), total_books_rented=12, date_expiration=date(2020, 12, 30), number_of_rented_books=0)        
            
    db.session.add(member1)
    db.session.add(member2)
    db.session.add(member3)
    db.session.add(member4)
    db.session.add(member5)
    db.session.add(member6)
    db.session.add(member7)        
    
    book1 = Book(id=1, signature='21.125-123-55', inv_number='12', title='Derviš i smrt', author='Meša Selimović', is_rented=True, has_error=False)
    book2 = Book(id=2, signature='21.125-123-55', inv_number='45', title='Prokleta avlija', author='Ivo Andrić', is_rented=True, has_error=False)
    book3 = Book(id=3, signature='21.125-123-76', inv_number='76', title='Znamenje anđela', author='Dejan Stojiljković', is_rented=True, has_error=False)
    book4 = Book(id=4, signature='23.543-321-77', inv_number='104', title='Olujni bedem', author='Dejan Stojiljković', is_rented=False, has_error=False)
    book5 = Book(id=5, signature='64.243-987-02', inv_number='175', title='Stefan Prvovenčani', author='Luka Mičeta', is_rented=True, has_error=False)
    book6 = Book(id=6, signature='64.243-879-27', inv_number='176', title='Stefan Nemanja', author='Luka Mičeta', is_rented=False, has_error=False)
    book7 = Book(id=7, signature='18.723-908-41', inv_number='608', title='Savršeno sećanje na smrt', author='Radoslav Petković', is_rented=False, has_error=False)
    book8 = Book(id=8, signature='15.127-436-13', inv_number='732', title='Simeonov pečat', author='Vanja Bulić', is_rented=True, has_error=False)
    book9 = Book(id=9, signature='96.598-702-48', inv_number='732', title='Dnevnik jednog čarobnjaka', author='Paolo Koeljo', is_rented=False, has_error=True)
    book10 = Book(id=10, signature='15.127-809-43', inv_number='1004', title='Kada govori mrtav kralj', author='Ivan Miladinović', is_rented=True, has_error=False)
    book11 = Book(id=11, signature='74.183-704-33', inv_number='3298', title='Nulta krvna grupa', author='Slavko Nikić', is_rented=True, has_error=False)
    book12 = Book(id=12, signature='96.598-702-48', inv_number='3305', title='Peta Gora', author='Paolo Koeljo', is_rented=False, has_error=False)
    book13 = Book(id=13, signature='38.563-123-78', inv_number='6987', title='Komitet 300', author='Džon Kolman', is_rented=True, has_error=False)
    book14 = Book(id=14, signature='96.598-702-48', inv_number='10238', title='Peta Gora', author='Paolo Koeljo', is_rented=True, has_error=False)  

    db.session.add(book1)
    db.session.add(book2)
    db.session.add(book3)
    db.session.add(book4)
    db.session.add(book5)
    db.session.add(book6)
    db.session.add(book7)
    db.session.add(book8)
    db.session.add(book9)
    db.session.add(book10)
    db.session.add(book11)
    db.session.add(book12)
    db.session.add(book13)
    db.session.add(book14)

    price1 = ExtensionPrice(id=1, price_value=10.00, currency='KM')
    price2 = ExtensionPrice(id=2, price_value=0.00, currency='KM', note="Besplatno")
    price3 = ExtensionPrice(id=3, price_value=7.99, currency='KM', note="Letnji popust", is_enabled=False)
    price4 = ExtensionPrice(id=4, price_value=14.00, currency='KM', note="Novogodišnja akcija - dve članarine", is_enabled=False)
    
    db.session.add(price1)
    db.session.add(price2)
    db.session.add(price3)
    db.session.add(price4)
  
    extensions = [
        Extension(note='', price=10.00, date_performed=date(1999, 3, 23), date_extended=date(1999, 3, 23), price_id=3, member_id=24, price_details=price3, member=member3),
        Extension(note='Učenik osnovne škole ne plaća članarinu', price=0.00, date_performed=date(2010, 1, 3), date_extended=date(2011, 1, 3), price_id=1, member_id=42, price_details=price1, member=member4),
        Extension(note='', price=10.00, date_performed=date(2011, 5, 12), date_extended=date(2012, 5, 12), price_id=3, member_id=18, price_details=price3, member=member2),
        Extension(note='Cena letnjeg popusta', price=7.99, date_performed=date(2012, 8, 14), date_extended=date(2013, 8, 14), price_id=2, member_id=103, price_details=price2, member=member6),
        Extension(note='Cena letnjeg popusta', price=7.99, date_performed=date(2012, 8, 14), date_extended=date(2013, 8, 14), price_id=2, member_id=104, price_details=price2, member=member7),
        Extension(note='Prva uplata', price=10.00, date_performed=date(2016, 2, 18), date_extended=date(2017, 2, 18), price_id=3, member_id=3, price_details=price3, member=member1),
        Extension(note='', price=10.00, date_performed=date(2017, 9, 28), date_extended=date(2018, 9, 28), price_id=3, member_id=3, price_details=price3, member=member1),
        Extension(note='Redovno produženje članarine', price=10.00, date_performed=date(2018, 9, 21), date_extended=date(2019, 9, 28), price_id=3, member_id=3, price_details=price3, member=member1),
        Extension(note='Učenik osnovne škole ne plaća članarinu', price=0.00, date_performed=date(2018, 10, 7), date_extended=date(2019, 10, 7), price_id=1, member_id=42, price_details=price1, member=member4),
        Extension(note='Produženje, cena redovna', price=10.00, date_performed=date(2019, 5, 25), date_extended=date(2020, 5, 25), price_id=3, member_id=24, price_details=price3, member=member3),
        Extension(note='Cena letnjeg popusta', price=7.99, date_performed=date(2019, 7, 23), date_extended=date(2020, 7, 23), price_id=2, member_id=76, price_details=price2, member=member5),
        Extension(note='Član 104 ne plaća jer ovaj član plaća iznos akcije', price=14.00, date_performed=date(2019, 12, 30), date_extended=date(2020, 12, 30), price_id=4, member_id=103, price_details=price4, member=member6),
        Extension(note='Ovaj član ne plaća članarinu, jer član 103 plaća iznos akcije', price=0.00, date_performed=date(2019, 12, 30), date_extended=date(2020, 12, 30), price_id=1, member_id=104, price_details=price1, member=member7),
        Extension(note='', price=10.00, date_performed=date(2020, 2, 24), date_extended=date(2021, 2, 24), price_id=3, member_id=3, price_details=price3, member=member1)]
           
    for extension in extensions:
        db.session.add(extension)

    rents = [
        Rental(date_performed=date(1999, 8, 8), date_deadline=date(1999, 8, 22), date_termination=date(1999, 8, 31), is_terminated=True, book_id=3, member_id=24, book=book3, member=member3),
        Rental(date_performed=date(2010, 2, 16), date_deadline=date(2010, 3, 2), date_termination=date(2010, 3, 12), is_terminated=True, book_id=7, member_id=42, book=book7, member=member4),
        Rental(date_performed=date(2011, 5, 15), date_deadline=date(2011, 5, 29), date_termination=date(2011, 6, 29), is_terminated=True, book_id=6, member_id=18, book=book6, member=member2),
        Rental(date_performed=date(2011, 9, 28), date_deadline=date(2011, 10, 12), date_termination=date(2011, 12, 28), is_terminated=True, book_id=10, member_id=18, book=book10, member=member2),
        Rental(date_performed=date(2012, 3, 15), date_deadline=date(2012, 3, 29), date_termination=None, is_terminated=False, book_id=3, member_id=18, book=book3, member=member2),
        Rental(date_performed=date(2012, 8, 14), date_deadline=date(2012, 8, 28), date_termination=date(2012, 8, 25), is_terminated=True, book_id=2, member_id=103, book=book2, member=member6),
        Rental(date_performed=date(2016, 3, 19), date_deadline=date(2016, 4, 2), date_termination=date(2016, 4, 2), is_terminated=True, book_id=14, member_id=3, book=book14, member=member1),
        Rental(date_performed=date(2016, 6, 30), date_deadline=date(2016, 7, 14), date_termination=date(2016, 7, 6), is_terminated=True, book_id=8, member_id=3, book=book8, member=member1),
        Rental(date_performed=date(2018, 10, 7), date_deadline=date(2018, 10, 21), date_termination=date(2018, 10, 20), is_terminated=True, book_id=12, member_id=42, book=book12, member=member4),
        Rental(date_performed=date(2018, 12, 11), date_deadline=date(2018, 12, 25), date_termination=date(2019, 1, 12), is_terminated=True, book_id=2, member_id=3, book=book2, member=member1),
        Rental(date_performed=date(2019, 4, 16), date_deadline=date(2019, 4, 30), date_termination=date(2019, 4, 29), is_terminated=True, book_id=10, member_id=42, book=book10, member=member4),
        Rental(date_performed=date(2019, 10, 2), date_deadline=date(2019, 10, 16), date_termination=date(2019, 10, 15), is_terminated=True, book_id=7, member_id=76, book=book7, member=member5),
        Rental(date_performed=date(2019, 12, 16), date_deadline=date(2019, 12, 30), date_termination=date(2020, 2, 10), is_terminated=True, book_id=10, member_id=24, book=book10, member=member3),
        Rental(date_performed=date(2019, 12, 30), date_deadline=date(2020, 1, 13), date_termination=date(2020, 1, 9), is_terminated=True, book_id=1, member_id=103, book=book11, member=member6),
        Rental(date_performed=date(2020, 1, 13), date_deadline=date(2020, 1, 27), date_termination=date(2020, 1, 27), is_terminated=True, book_id=4, member_id=103, book=book4, member=member6),
        Rental(date_performed=date(2020, 1, 20), date_deadline=date(2020, 2, 3), date_termination=date(2020, 1, 31), is_terminated=True, book_id=13, member_id=103, book=book13, member=member6),
        Rental(date_performed=date(2020, 2, 1), date_deadline=date(2020, 2, 15), date_termination=None, is_terminated=False, book_id=8, member_id=103, book=book8, member=member6),
        Rental(date_performed=date(2020, 3, 18), date_deadline=date(2020, 4, 1), date_termination=None, is_terminated=False, book_id=10, member_id=76, book=book10, member=member5),
        Rental(date_performed=date.today()-timedelta(15), date_deadline=date.today()-timedelta(1), date_termination=None, is_terminated=False, book_id=11, member_id=3, book=book11, member=member1),
        Rental(date_performed=date.today()-timedelta(14), date_deadline=date.today(), date_termination=None, is_terminated=False, book_id=5, member_id=24, book=book5, member=member3),
        Rental(date_performed=date.today()-timedelta(10), date_deadline=date.today()+timedelta(4), date_termination=None, is_terminated=False, book_id=1, member_id=103, book=book1, member=member6),
        Rental(date_performed=date.today()-timedelta(5), date_deadline=date.today()+timedelta(9), date_termination=None, is_terminated=False, book_id=12, member_id=103, book=book12, member=member6),
        Rental(date_performed=date.today()-timedelta(1), date_deadline=date.today()+timedelta(13), date_termination=None, is_terminated=False, book_id=14, member_id=76, book=book14, member=member5),
        Rental(date_performed=date.today(), date_deadline=date.today()+timedelta(14), date_termination=None, is_terminated=False, book_id=2, member_id=103, book=book2, member=member6)]
        
    for rent in rents:
        db.session.add(rent)
    
    events = [
        Event(time=datetime(1998,2,12,8,12), type=41, librarian='djoka.djokic', message='Cena sa oznakom 1 i iznosom 0.00 KM je dodata.'),
        Event(time=datetime(1998,2,14,10,42), type=1, librarian='djoka.djokic', message='Knjiga sa oznakom 2 je dodata.'),
        Event(time=datetime(1998,2,14,10,53), type=1, librarian='djoka.djokic', message='Knjiga sa oznakom 3 je dodata.'),
        Event(time=datetime(1998,2,14,10,53), type=3, librarian='djoka.djokic', message='Knjiga sa oznakom 3 je označena sa greškom inventarnog broja koji je postavljen na "75"'),
        Event(time=datetime(1998,2,14,10,59), type=1, librarian='djoka.djokic', message='Knjiga sa oznakom 6 je dodata.'),
        Event(time=datetime(1998,2,14,11,4), type=1, librarian='djoka.djokic', message='Knjiga sa oznakom 7 je dodata.'),
        Event(time=datetime(1998,2,14,11,7), type=1, librarian='djoka.djokic', message='Knjiga sa oznakom 10 je dodata.'),
        Event(time=datetime(1998,3, 18,16, 4), type=21, librarian='djoka.djokic', message='Dodat je član, dodeljena mu je članska karta sa brojem 24.'),
        Event(time=datetime(1999, 3, 23,15,49), type=31, librarian='djoka.djokic', message='Članstvo je produženo za člana sa članskim brojem 24 po ceni od 10.00 KM.'),
        Event(time=datetime(1999, 8, 8,13,13), type=11, librarian='djoka.djokic', message='Knjiga sa oznakom 3 iznajmljena je članu sa članskim brojem 24.'),
        Event(time=datetime(1999, 8, 31,9,45), type=12, librarian='djoka.djokic', message='Knjiga sa oznakom 3 je vraćena od strane člana sa članskim brojem 24.'),
        Event(time=datetime(2001,5,17,10,21), type=41, librarian='djoka.djokic', message='Cena sa oznakom 2 i iznosom 0.00 KM je dodata.'),            
        Event(time=datetime(2005,4,29,13,43), type=52, librarian='djoka.djokic', message='Bibliotekar je promeio svoju lozinku.'),
        Event(time=datetime(2006,5,16,8,52), type=50, librarian='djoka.djokic', message='Bibliotekar sa korisničkim imenom mika.mikic je dodat.'),
        Event(time=datetime(2006,8,11,14,52), type=22, librarian='djoka.djokic', message='Izmenjeni su podaci člana sa brojem članske karte 24 i to "Telefon" iz "059233452" u "0654433565".'),
        Event(time=datetime(2008,8,20,15,15), type=51, librarian='mika.mikic', message='Bibliotekar je promenio sledeći podatak "Adresa" iz "Dobrovoljačka 21, Nevesinje" u "Milivoja Mikića 3, Nevesinje"'),        
        Event(time=datetime(2008,10,27, 8,49), type=21, librarian='mika.mikic', message='Dodat je član, dodeljena mu je članska karta sa brojem 42.'),
        Event(time=datetime(2010, 1, 3,13,40), type=31, librarian='mika.mikic', message='Članstvo je produženo za člana sa članskim brojem 42 po ceni od 0.00 KM.'),
        Event(time=datetime(2010, 2,16,10,54), type=11, librarian='mika.mikic', message='Knjiga sa oznakom 7 iznajmljena je članu sa članskim brojem 42.'),
        Event(time=datetime(2010, 3,12,11,59), type=12, librarian='mika.mikic', message='Knjiga sa oznakom 7 je vraćena od strane člana sa članskim brojem 42.'),
        Event(time=datetime(2011,5, 12, 8,8), type=21, librarian='djoka.djokic', message='Dodat je član, dodeljena mu je članska karta sa brojem 18.'),
        Event(time=datetime(2011, 5, 12,8,16), type=31, librarian='djoka.djokic', message='Članstvo je produženo za člana sa članskim brojem 18 po ceni od 10.00 KM.'),
        Event(time=datetime(2011, 5,15, 9,23), type=11, librarian='mika.mikic', message='Knjiga sa oznakom 6 iznajmljena je članu sa članskim brojem 18.'),
        Event(time=datetime(2011, 6,29,15,27), type=12, librarian='mika.mikic', message='Knjiga sa oznakom 6 je vraćena od strane člana sa članskim brojem 18.'),
        Event(time=datetime(2011, 9,28,16,41), type=11, librarian='djoka.djokic', message='Knjiga sa oznakom 10 iznajmljena je članu sa članskim brojem 18.'),
        Event(time=datetime(2011,12,28,14,10), type=12, librarian='djoka.djokic', message='Knjiga sa oznakom 10 je vraćena od strane člana sa članskim brojem 18.'),
        Event(time=datetime(2012, 3,15,15,20), type=11, librarian='mika.mikic', message='Knjiga sa oznakom 3 iznajmljena je članu sa članskim brojem 18.'),
        Event(time=datetime(2012, 8, 1,9,7), type=41, librarian='djoka.djokic', message='Cena sa oznakom 3 i iznosom 7.99 KM je dodata.'),
        Event(time=datetime(2012,8, 14,10,20), type=21, librarian='mika.mikic', message='Dodat je član, dodeljena mu je članska karta sa brojem 103.'),
        Event(time=datetime(2012,8, 14,10,26), type=21, librarian='mika.mikic', message='Dodat je član, dodeljena mu je članska karta sa brojem 104.'),
        Event(time=datetime(2012, 8, 14,10,31), type=31, librarian='djoka.djokic', message='Članstvo je produženo za člana sa članskim brojem 103 po ceni od 7.99 KM.'),
        Event(time=datetime(2012, 8, 14,10,32), type=31, librarian='mika.mikic', message='Članstvo je produženo za člana sa članskim brojem 104 po ceni od 7.99 KM.'),
        Event(time=datetime(2012, 8,14,11,24), type=11, librarian='djoka.djokic', message='Knjiga sa oznakom 2 iznajmljena je članu sa članskim brojem 103.'),
        Event(time=datetime(2012, 8, 25,8,31), type=12, librarian='mika.mikic', message='Knjiga sa oznakom 2 je vraćena od strane člana sa članskim brojem 103.'),
        Event(time=datetime(2012, 9,30,8,48), type=43, librarian='djoka.djokic', message='Cena sa oznakom 3 i iznosom 7.99 KM je deaktivirana.'),
        Event(time=datetime(2012,12,1,9,12), type=41, librarian='djoka.djokic', message='Cena sa oznakom 4 i iznosom 14.00 KM je dodata.'),
        Event(time=datetime(2012,12,4,9,4), type=50, librarian='djoka.djokic', message='Bibliotekar sa korisničkim imenom pera.peric je dodat.'),  
        Event(time=datetime(2012,12,4,10,43), type=57, librarian='djoka.djokic', message='Administrator je dodao bibliotekara sa korisničkim imenom pera.peric u administratore.'),
        Event(time=datetime(2012,12,29,14,32), type=58, librarian='pera.peric', message='Administrator je poslao zahtev da administrator sa korisničkim imenom djoka.djokic bude isključen iz grupe administratora.'),
        Event(time=datetime(2012,12,30,9,37), type=59, librarian='djoka.djokic', message='Administrator je prihvatio zahtev da bude isključen iz grupe administratora.'),
        Event(time=datetime(2013,1,5,8,27), type=56, librarian='pera.peric', message='Bibliotekar sa korisničkim imenom djoka.djokic je postavljen kao neaktivan.'),
        Event(time=datetime(2014,5,12,13,46), type=1, librarian='pera.peric', message='Knjiga sa oznakom 8 je dodata.'),
        Event(time=datetime(2014,5,12,13,53), type=1, librarian='pera.peric', message='Knjiga sa oznakom 12 je dodata.'),
        Event(time=datetime(2014,5,12,14,2), type=1, librarian='pera.peric', message='Knjiga sa oznakom 14 je dodata.'),  
        Event(time=datetime(2014,5,12,14,11), type=2, librarian='pera.peric', message='Knjizi sa oznakom 3 je izmenjen sledeći podatak "Inventarni broj" iz "75" u "76"'),  
        Event(time=datetime(2014,5,12,14,11), type=4, librarian='pera.peric', message='Knjizi sa oznakom 3 je ispravljena greška inventarnog broja.'),
        Event(time=datetime(2014,8,21,12,31), type=1, librarian='mika.mikic', message='Knjiga sa oznakom 1 je dodata.'),     
        Event(time=datetime(2014,8,21,12,31), type=3, librarian='mika.mikic', message='Knjiga sa oznakom 1 je označena sa greškom inventarnog broja koji je postavljen na "11"'),
        Event(time=datetime(2014,8,22,9,29), type=2, librarian='pera.peric', message='Knjizi sa oznakom 1 je izmenjen sledeći podatak "Inventarni broj" iz "11" u "12"'),
        Event(time=datetime(2014,8,22,9,29), type=4, librarian='pera.peric', message='Knjizi sa oznakom 1 je ispravljena greška inventarnog broja.'),    
        Event(time=datetime(2015,6,1,10,00), type=42, librarian='pera.peric', message='Cena sa oznakom 3 i iznosom 7.99 KM je aktivirana.'),
        Event(time=datetime(2015,9,30,9,42), type=43, librarian='pera.peric', message='Cena sa oznakom 3 i iznosom 7.99 KM je deaktivirana.'),
        Event(time=datetime(2016,2, 18,9,21), type=21, librarian='pera.peric', message='Dodat je član, dodeljena mu je članska karta sa brojem 3.'),
        Event(time=datetime(2016, 2, 18,9,27), type=31, librarian='pera.peric', message='Članstvo je produženo za člana sa članskim brojem 3 po ceni od 10.00 KM.'),
        Event(time=datetime(2016, 3,19,12,15), type=11, librarian='mika.mikic', message='Knjiga sa oznakom 14 iznajmljena je članu sa članskim brojem 3.'),
        Event(time=datetime(2016, 4, 2,15,42), type=12, librarian='pera.peric', message='Knjiga sa oznakom 14 je vraćena od strane člana sa članskim brojem 3.'),
        Event(time=datetime(2016, 6,30,14,42), type=11, librarian='mika.mikic', message='Knjiga sa oznakom 8 iznajmljena je članu sa članskim brojem 3.'),
        Event(time=datetime(2016, 7, 6,16,47), type=12, librarian='mika.mikic', message='Knjiga sa oznakom 8 je vraćena od strane člana sa članskim brojem 3.'),
        Event(time=datetime(2016,11,15,15,34), type=52, librarian='pera.peric', message='Bibliotekar je promeio svoju lozinku.'),
        Event(time=datetime(2017,7,18,15,42), type=51, librarian='mika.mikic', message='Bibliotekar je promenio sledeći podatak "Telefon" iz "+387663227893" u "+387664408404"'),
        Event(time=datetime(2017, 9, 28,11,18), type=31, librarian='pera.peric', message='Članstvo je produženo za člana sa članskim brojem 3 po ceni od 10.00 KM.'),
        Event(time=datetime(2017,10,11,9,15), type=1, librarian='pera.peric', message='Knjiga sa oznakom 11 je dodata.'),
        Event(time=datetime(2017,10,11,9,21), type=1, librarian='mika.mikic', message='Knjiga sa oznakom 4 je dodata.'),
        Event(time=datetime(2017,10,11,9,23), type=1, librarian='pera.peric', message='Knjiga sa oznakom 13 je dodata.'),
        Event(time=datetime(2017,10,11,9,28), type=1, librarian='mika.mikic', message='Knjiga sa oznakom 5 je dodata.'),
        Event(time=datetime(2017,10,11,9,29), type=2, librarian='pera.peric', message='Knjizi sa oznakom 6 je izmenjen sledeći podatak "Naslov" iz "Stefan Nemenja" u "Stefan Nemanja".'),
        Event(time=datetime(2017,10,11,9,34), type=2, librarian='pera.peric', message='Knjizi sa oznakom 10 je izmenjen sledeći podatak "Autor" iz "Ivan Mladenović" u "Ivan Miladinović".'),
        Event(time=datetime(2017,11,23,14,31), type=1, librarian='mika.mikic', message='Knjiga sa oznakom 9 je dodata.'),
        Event(time=datetime(2017,11,23,14,31), type=3, librarian='mika.mikic', message='Knjiga sa oznakom 9 je označena sa greškom inventarnog broja koji je postavljen na "732"'),
        Event(time=datetime(2018,3,21,15,29), type=51, librarian='pera.peric', message='Bibliotekar je promenio sledeći podatak "Telefon" iz "0650990179" u "0651128767"'),
        Event(time=datetime(2018,8,7,11,47), type=52, librarian='pera.peric', message='Bibliotekar je promeio svoju lozinku.'),
        Event(time=datetime(2018, 9, 21,16,11), type=31, librarian='mika.mikic', message='Članstvo je produženo za člana sa članskim brojem 3 po ceni od 10.00 KM.'),
        Event(time=datetime(2018, 10,7,9,57), type=11, librarian='mika.mikic', message='Knjiga sa oznakom 12 iznajmljena je članu sa članskim brojem 42.'),
        Event(time=datetime(2018, 10, 7,14,6), type=31, librarian='mika.mikic', message='Članstvo je produženo za člana sa članskim brojem 42 po ceni od 0.00 KM.'),
        Event(time=datetime(2018,10,13,10,52), type=56, librarian='pera.peric', message='Bibliotekar sa korisničkim imenom mika.mikic je postavljen kao neaktivan.'),
        Event(time=datetime(2018, 10, 20,9,8), type=12, librarian='pera.peric', message='Knjiga sa oznakom 12 je vraćena od strane člana sa članskim brojem 42.'),
        Event(time=datetime(2018,10,26,10,11), type=22, librarian='pera.peric', message='Izmenjeni su podaci člana sa brojem članske karte 3 i to "Zanimanje" iz "student" u "dip. Ekonomista".'),
        Event(time=datetime(2018,12,3,9,48), type=55, librarian='pera.peric', message='Bibliotekar sa korisničkim imenom mika.mikic je postavljen kao aktivan.'),    
        Event(time=datetime(2018,12,4,8,24), type=53, librarian='mika.mikic', message='Bibliotekar je poslao zahtev za promenu lozinke.'),
        Event(time=datetime(2018,12,4,9,48), type=54, librarian='pera.peric', message='Administrator je odgovorio na zahtev i promenio lozinku bibliotekara.'),
        Event(time=datetime(2018,12,4,9,54), type=52, librarian='mika.mikic', message='Bibliotekar je promeio svoju lozinku.'),
        Event(time=datetime(2018,12,11,10,18), type=11, librarian='pera.peric', message='Knjiga sa oznakom 2 iznajmljena je članu sa članskim brojem 3.'),
        Event(time=datetime(2019, 1,12,11,19), type=12, librarian='mika.mikic', message='Knjiga sa oznakom 2 je vraćena od strane člana sa članskim brojem 3.'),
        Event(time=datetime(2019, 4,16,11,40), type=11, librarian='pera.peric', message='Knjiga sa oznakom 10 iznajmljena je članu sa članskim brojem 42.'),
        Event(time=datetime(2019, 4, 29,8,52), type=12, librarian='pera.peric', message='Knjiga sa oznakom 10 je vraćena od strane člana sa članskim brojem 42.'),
        Event(time=datetime(2019, 5, 25,12,37), type=31, librarian='mika.mikic', message='Članstvo je produženo za člana sa članskim brojem 24 po ceni od 10.00 KM.'),
        Event(time=datetime(2019,6,1,9,19), type=42, librarian='pera.peric', message='Cena sa oznakom 3 i iznosom 7.99 KM je aktivirana.'),
        Event(time=datetime(2019,7, 23,9,31), type=21, librarian='mika.mikic', message='Dodat je član, dodeljena mu je članska karta sa brojem 76.'),
        Event(time=datetime(2019, 7, 23,9,42), type=31, librarian='pera.peric', message='Članstvo je produženo za člana sa članskim brojem 76 po ceni od 7.99 KM.'),
        Event(time=datetime(2019,9,20,8,31), type=43, librarian='pera.peric', message='Cena sa oznakom 3 i iznosom 7.99 KM je deaktivirana.'),
        Event(time=datetime(2019,10, 2,13,38), type=11, librarian='mika.mikic', message='Knjiga sa oznakom 7 iznajmljena je članu sa članskim brojem 76.'),
        Event(time=datetime(2019,10,15,14,33), type=12, librarian='mika.mikic', message='Knjiga sa oznakom 7 je vraćena od strane člana sa članskim brojem 76.'),
        Event(time=datetime(2019,12,1,9,3), type=42, librarian='pera.peric', message='Cena sa oznakom 4 i iznosom 14.00 KM je aktivirana.'),
        Event(time=datetime(2019,12,16,15,36), type=11, librarian='pera.peric', message='Knjiga sa oznakom 10 iznajmljena je članu sa članskim brojem 24.'),
        Event(time=datetime(2019, 12,30,10,9), type=31, librarian='pera.peric', message='Članstvo je produženo za člana sa članskim brojem 103 po ceni od 14.00 KM.'),
        Event(time=datetime(2019, 12,30,10,10), type=31, librarian='mika.mikic', message='Članstvo je produženo za člana sa članskim brojem 104 po ceni od 0.00 KM.'),
        Event(time=datetime(2019,12,30,10,12), type=11, librarian='mika.mikic', message='Knjiga sa oznakom 1 iznajmljena je članu sa članskim brojem 103.'),
        Event(time=datetime(2020, 1, 9,15,45), type=12, librarian='pera.peric', message='Knjiga sa oznakom 1 je vraćena od strane člana sa članskim brojem 103.'),
        Event(time=datetime(2020, 1,13,16,4), type=11, librarian='pera.peric', message='Knjiga sa oznakom 4 iznajmljena je članu sa članskim brojem 103.'),
        Event(time=datetime(2020, 1,20, 9,39), type=11, librarian='pera.peric', message='Knjiga sa oznakom 13 iznajmljena je članu sa članskim brojem 103.'),
        Event(time=datetime(2020, 1,27,16,20), type=12, librarian='pera.peric', message='Knjiga sa oznakom 4 je vraćena od strane člana sa članskim brojem 103.'),
        Event(time=datetime(2020, 1,31,12,13), type=12, librarian='mika.mikic', message='Knjiga sa oznakom 13 je vraćena od strane člana sa članskim brojem 103.'),
        Event(time=datetime(2020, 2,1,8,38), type=43, librarian='pera.peric', message='Cena sa oznakom 4 i iznosom 14.00 KM je deaktivirana.'),
        Event(time=datetime(2020, 2, 1, 8,41), type=11, librarian='mika.mikic', message='Knjiga sa oznakom 8 iznajmljena je članu sa članskim brojem 103.'),
        Event(time=datetime(2020, 2, 10,12,5), type=12, librarian='mika.mikic', message='Knjiga sa oznakom 10 je vraćena od strane člana sa članskim brojem 24.'),
        Event(time=datetime(2020, 2, 24,12,15), type=31, librarian='pera.peric', message='Članstvo je produženo za člana sa članskim brojem 3 po ceni od 10.00 KM.'),
        Event(time=datetime(2020, 3,18,14,29), type=11, librarian='pera.peric', message='Knjiga sa oznakom 10 iznajmljena je članu sa članskim brojem 76.'),
        Event(time=datetime(2020,date.today().month,date.today().day,12,33)-timedelta(15), type=11, librarian='pera.peric', message='Knjiga sa oznakom 11 iznajmljena je članu sa članskim brojem 3.'),
        Event(time=datetime(2020,date.today().month,date.today().day,11,56)-timedelta(14), type=11, librarian='mika.mikic', message='Knjiga sa oznakom 5 iznajmljena je članu sa članskim brojem 24.'),
        Event(time=datetime(2020,date.today().month,date.today().day,9,2)-timedelta(10), type=11, librarian='pera.peric', message='Knjiga sa oznakom 1 iznajmljena je članu sa članskim brojem 103.'),
        Event(time=datetime(2020,date.today().month,date.today().day,16,48)-timedelta(5), type=11, librarian='mika.mikic', message='Knjiga sa oznakom 12 iznajmljena je članu sa članskim brojem 103.'),
        Event(time=datetime(2020,date.today().month,date.today().day,13,7)-timedelta(1), type=11, librarian='mika.mikic', message='Knjiga sa oznakom 14 iznajmljena je članu sa članskim brojem 76.'),
        Event(time=datetime(2020,date.today().month,date.today().day, 8,30), type=11, librarian='pera.peric', message='Knjiga sa oznakom 2 iznajmljena je članu sa članskim brojem 103.')]
  
  
  
  
    for event in events:
        db.session.add(event)
    
    db.session.commit()
