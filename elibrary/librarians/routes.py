from flask import render_template, url_for, redirect, request, flash, Blueprint, abort
from flask_login import login_user, current_user, logout_user, login_required
from flask_babel import gettext, lazy_gettext as _l
from elibrary import bcrypt, db
from elibrary.librarians.forms import (LibrarianCreateForm, LibrarianUpdateForm, LoginForm,
        LibrarianUpdatePasswordForm, LibrarianChangePasswordForm, LibrarianRequestChangePasswordForm)
from elibrary.main.forms import AcceptForm, RejectForm
from elibrary.models import Librarian
from sqlalchemy import desc

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
        current_user.phone = form.phone.data.replace("/", "")
        current_user.address = form.address.data
        if not (current_user.username == form.username.data or form.username.data==''):
            current_user.change_username_value = form.username.data
            flash(_l('A username change request has been created')+'.', 'success')
        db.session.commit()
        flash(_l('Account has been updated')+'.', 'success')
        return redirect(url_for('librarians.account'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
        form.phone.data = current_user.phone_formated
        form.address.data = current_user.address
    return render_template('account_cu.html', form=form, admin_is_editing=False, is_creating=False)

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


@librarians.route("/librarians")
@login_required
def librarianss():
    if not current_user.is_admin:
        abort(403)
    include_inactive = request.args.get('include_inactive', 'False', type=str)
    sort_criteria = request.args.get('sort_by', 'first_name', type=str)
    sort_direction = request.args.get('direction', 'up', type=str)
    include_disabled_val=True
    filter_args = {'include_inactive': 'True'}
    my_query = db.session.query(Librarian)
    if include_inactive == 'False':
        my_query = my_query.filter(Librarian.is_operational)
        include_disabled_val=False
        filter_args['include_inactive']='False'
    if sort_direction == 'up':
        list = my_query.order_by(sort_criteria).all()
    else:
        list = my_query.order_by(desc(sort_criteria)).all()
    return render_template('librarians.html', librarians_list=list, include_disabled=include_disabled_val, extra_filter_args=filter_args)

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
        librarian.phone = form.phone.data.replace("/", "")
        librarian.address = form.address.data
        librarian.date_registered = form.date_registered.data
        librarian.username = form.username.data
        librarian.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        librarian.is_admin = form.is_administrator.data
        db.session.add(librarian)
        db.session.commit()
        flash(_l('Account has been created')+'.', 'success')
        return redirect(url_for('librarians.librarians_active'))
    return render_template('account_cu.html', form=form, is_creating=True)

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
        librarian.phone = form.phone.data.replace("/", "")
        librarian.address = form.address.data
        db.session.commit()
        flash(_l('Account has been updated')+'.', 'success')
        return redirect(url_for('librarians.librarians_details',librarian_id=librarian.id))
    elif request.method == 'GET':
        form.first_name.data = librarian.first_name
        form.last_name.data = librarian.last_name
        form.email.data = librarian.email
        form.phone.data = librarian.phone_formated
        form.address.data = librarian.address
    return render_template('account_cu.html', form=form, admin_is_editing=True, is_creating=False)

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
