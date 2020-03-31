from flask import render_template, url_for, redirect, request, flash, Blueprint, abort
from flask_login import login_user, current_user, logout_user, login_required
from flask_babel import gettext, lazy_gettext as _l
from elibrary import bcrypt, db
from elibrary.librarians.forms import (LibrarianCreateForm, LibrarianUpdateForm, LoginForm,
        LibrarianUpdatePasswordForm, LibrarianChangePasswordForm, LibrarianRequestChangePasswordForm)
from elibrary.main.forms import AcceptForm, RejectForm
from elibrary.models import Librarian

librarians = Blueprint('librarians', __name__)

@librarians.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('librarians.login'))

@librarians.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        admin = Librarian.query.filter_by(username=form.username.data).first()
        if admin:
            if admin.is_operational and bcrypt.check_password_hash(admin.password, form.password.data):
                login_user(admin)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.home'))
            else:
                flash(_l('Login Unsuccessful')+'. '+_l('This user is inactive')+'.', 'danger')
                flash(_l('For the activation consult the administrator')+'. ', 'danger')
        else:
            flash(_l('Login Unsuccessful')+'. '+_l('Please check username and password')+'.', 'danger')
    form.username.data=''
    return render_template('login.html', title=_l('Login'), form=form)

@librarians.route("/login/password", methods=['GET', 'POST'])
def login_password_reset():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LibrarianRequestChangePasswordForm()
    if form.validate_on_submit():
        librarian = Librarian.query.filter_by(username=form.username.data).first()
        if librarian:
            if librarian.first_name == form.first_name.data and librarian.last_name == form.last_name.data:
                librarian.change_password = True
                db.session.commit()
                flash(_l('Reset password request has been sent to the administrator')+'.', 'success')
                return redirect(url_for('librarians.login'))
        flash(_l('Combination of the username, first and last name does not exist')+'.', 'error')
        flash(_l('Please check your input and try again')+'.', 'error')
    form.username.data=''
    form.first_name.data=''
    form.last_name.data=''
    return render_template('login_password_reset.html', form=form, title=_l('Password Change Request'))


@librarians.route("/account")
@login_required
def account():
    return render_template('account.html', account=current_user, title=_l('My account'), admin_is_editing=False)

@librarians.route("/account/change", methods=['GET', 'POST'])
@login_required
def account_change():
    form = LibrarianUpdateForm()
    if form.validate_on_submit():
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.email = form.email.data
        current_user.phone_1 = form.phone_1.data
        current_user.phone_2 = form.phone_2.data
        current_user.address = form.address.data
        current_user.town = form.town.data
        if not current_user.username == form.username.data:
            current_user.change_username = True
            current_user.change_username_value = form.username.data
            flash(_l('A username change request has been created')+'.', 'success')
        db.session.commit()
        flash(_l('Account has been updated')+'.', 'success')
        return redirect(url_for('librarians.account'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
        form.phone_1.data = current_user.phone_1
        form.phone_2.data = current_user.phone_2
        form.address.data = current_user.address
        form.town.data = current_user.town
    return render_template('account_change.html', form=form, admin_is_editing=False)

@librarians.route("/account/password", methods=['GET', 'POST'])
@login_required
def account_password():
    form = LibrarianUpdatePasswordForm()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, form.old_password.data):
            current_user.password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            current_user.change_password = False
            db.session.commit()
            flash(_l('Account password has been updated')+'.', 'success')
            return redirect(url_for('librarians.account'))
        else:
            flash(_l('Current password value is not correct')+'.', 'error')
    return render_template('account_password_change.html', form=form)


@librarians.route("/librarians/all")
@login_required
def librarians_all():
    if not current_user.is_admin:
        abort(403)
    list = Librarian.query.order_by('first_name').all()
    return render_template('librarians.html', librarians_list=list, include_disabled=True)

@librarians.route("/librarians/active")
@login_required
def librarians_active():
    if not current_user.is_admin:
        abort(403)
    list = Librarian.query.filter(Librarian.is_operational).order_by('first_name').all()
    return render_template('librarians.html', librarians_list=list, include_disabled=False)

@librarians.route("/librarians/details/<int:librarian_id>")
@login_required
def librarians_details(librarian_id):
    if not current_user.is_admin:
        abort(403)
    librarian = Librarian.query.get_or_404(librarian_id)
    return render_template('account.html', account=librarian, title=_l('Account details'), admin_is_editing=True)


@librarians.route("/librarians/create", methods=['GET', 'POST'])
@login_required
def librarians_create():
    if not current_user.is_admin:
        abort(403)
    form = LibrarianCreateForm()
    if form.validate_on_submit():
        librarian = Librarian()
        librarian.first_name = form.first_name.data
        librarian.last_name = form.last_name.data
        librarian.email = form.email.data
        librarian.phone_1 = form.phone_1.data
        librarian.phone_2 = form.phone_2.data
        librarian.address = form.address.data
        librarian.town = form.town.data
        librarian.date_registered = form.date_registered.data
        librarian.username = form.username.data
        librarian.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        librarian.is_admin = form.is_administrator.data
        db.session.add(librarian)
        db.session.commit()
        flash(_l('Account has been created')+'.', 'success')
        return redirect(url_for('librarians.librarians_active'))
    return render_template('account_create.html', form=form)

@librarians.route("/librarians/update/<int:librarian_id>", methods=['GET', 'POST'])
@login_required
def librarians_update(librarian_id):
    if not current_user.is_admin:
        abort(403)
    librarian = Librarian.query.get_or_404(librarian_id)
    if librarian.id == current_user.id:
        return redirect(url_for('librarians.account_change'))
    form = LibrarianUpdateForm()
    if form.validate_on_submit():
        librarian.first_name = form.first_name.data
        librarian.last_name = form.last_name.data
        librarian.email = form.email.data
        librarian.phone_1 = form.phone_1.data
        librarian.phone_2 = form.phone_2.data
        librarian.address = form.address.data
        librarian.town = form.town.data
        db.session.commit()
        flash(_l('Account has been updated')+'.', 'success')
        return redirect(url_for('librarians.librarians_details',librarian_id=librarian.id))
    elif request.method == 'GET':
        form.first_name.data = librarian.first_name
        form.last_name.data = librarian.last_name
        form.email.data = librarian.email
        form.phone_1.data = librarian.phone_1
        form.phone_2.data = librarian.phone_2
        form.address.data = librarian.address
        form.town.data = librarian.town
    return render_template('account_change.html', form=form, admin_is_editing=True)

@librarians.route("/librarians/password/<int:librarian_id>", methods=['GET', 'POST'])
@login_required
def librarians_password(librarian_id):
    if not current_user.is_admin:
        abort(403)
    librarian = Librarian.query.get_or_404(librarian_id)
    if librarian.id == current_user.id:
        return redirect(url_for('librarians.account_password'))
    elif not librarian.change_password:
        abort(405)
    form = LibrarianChangePasswordForm()
    if form.validate_on_submit():
        librarian.password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
        librarian.change_password = False
        db.session.commit()
        flash(_l('Account password has been updated')+'.', 'success')
        return redirect(url_for('librarians.librarians_details', librarian_id=librarian.id))
    return render_template('account_password_change_request.html', form=form, librarian=librarian)

@librarians.route("/librarians/username/<int:librarian_id>", methods=['GET', 'POST'])
@login_required
def librarians_username(librarian_id):
    if not current_user.is_admin:
        abort(403)
    librarian = Librarian.query.get_or_404(librarian_id)
    if not librarian.change_username:
        abort(405)
    form_accept = AcceptForm()
    form_reject = RejectForm()
    if not request.method == 'GET':
        if form_reject.submit_reject.data and form_reject.validate():
            flash(_l('Account username change has been rejected')+'.', 'info')
        elif form_accept.submit_accept.data and form_accept.validate():
            user = Librarian.query.filter_by(username=librarian.change_username_value).first()
            if not user:
                librarian.username = librarian.change_username_value
                flash(_l('Account username has been changed')+'.', 'info')
            else:
                flash(_l('Username change has been rejected')+'.', 'info')
                flash(_l('Requested username is already in use')+'.', 'info')
        librarian.change_username = False
        librarian.change_username_value = None
        db.session.commit()
        return redirect(url_for('librarians.librarians_active'))
    return render_template('account_username_change_request.html', form1=form_accept, form2=form_reject, librarian=librarian)

@librarians.route("/librarians/availability/<int:librarian_id>", methods=['GET', 'POST'])
@login_required
def librarians_availability(librarian_id):
    if not current_user.is_admin:
        abort(403)
    librarian = Librarian.query.get_or_404(librarian_id)
    if current_user.id == librarian_id:
        abort(405)
    form_accept = AcceptForm()
    form_reject = RejectForm()
    if not request.method == 'GET':
        if form_reject.submit_reject.data and form_reject.validate():
            flash(_l('Account availability is not changed')+'.', 'info')
        elif form_accept.submit_accept.data and form_accept.validate():
            librarian.is_operational = not librarian.is_operational
            flash(_l('Account availability is changed')+'.', 'info')
        db.session.commit()
        return redirect(url_for('librarians.librarians_active'))
    return render_template('account_availability.html', form1=form_accept, form2=form_reject, librarian=librarian)
