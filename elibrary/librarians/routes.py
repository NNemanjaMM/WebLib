from flask import render_template, url_for, redirect, request, flash, Blueprint, abort
from flask_login import login_user, current_user, logout_user, login_required
from flask_babel import gettext as _g
from elibrary import bcrypt, db
from elibrary.librarians.forms import (LibrarianCreateForm, LibrarianUpdateForm, LoginForm,
        LibrarianUpdatePasswordForm, LibrarianChangePasswordForm, LibrarianRequestChangePasswordForm)
from elibrary.utils.defines import DATE_FORMAT
from elibrary.utils.common import EventWriter
from elibrary.main.forms import AcceptRejectForm
from elibrary.models import Librarian, EventType
from sqlalchemy import desc

librarians = Blueprint('librarians', __name__)
sort_librarian_values = ['first_name', 'last_name', 'date_registered']

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
            if admin.is_active and bcrypt.check_password_hash(admin.password, form.password.data):
                login_user(admin)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('main.home'))
            else:
                flash(_g('Login unsuccessfull')+'. ', 'danger')
                flash(_g('This user is inactive. For the activation consult the administrator.'), 'danger')
        else:
            flash(_g('Login unsuccessfull')+'. '+_g('Please check username and password')+'.', 'danger')
    form.username.data=''
    return render_template('login.html', title=_g('Login'), form=form)

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
                EventWriter.write_user(EventType.librarian_password_request, librarian.id, _g('Following librarian requested password change')+' ('+_g('Librarian username')+': '+librarian.username+'):'+librarian.log_data(), librarian.username)
                db.session.commit()
                flash(_g('Reset password request is successfully sent to the administrator')+'.', 'success')
                return redirect(url_for('librarians.login'))
        flash(_g('Combination of the username, first name and last name does not exist')+'.', 'error')
        flash(_g('Please check your input and try again')+'.', 'error')
    form.username.data=''
    form.first_name.data=''
    form.last_name.data=''
    return render_template('login_password_reset.html', form=form, title=_g('Password change request'))

@librarians.route("/account")
@login_required
def account():
    return render_template('account.html', account=current_user, admin_is_editing=False)

@librarians.route("/account/update", methods=['GET', 'POST'])
@login_required
def account_change():
    form = LibrarianUpdateForm()
    if form.validate_on_submit():
        if has_new_values(current_user, form):
            from_value = current_user.log_data()
            current_user.first_name = form.first_name.data
            current_user.last_name = form.last_name.data
            current_user.email = form.email.data
            current_user.phone = form.phone.data.replace("/", "")
            current_user.address = form.address.data
            EventWriter.write(EventType.librarian_update, current_user.id, _g('Following librarian account is updated')+' ('+_g('Librarian username')+': '+current_user.username+'):'+from_value+'<br/>'+_g('To new values')+':'+current_user.log_data())
            db.session.commit()
            flash(_g('Account data is successfully updated')+'.', 'success')
            return redirect(url_for('librarians.account'))
        else:
            flash(_g('Account data')+' '+_g('is not changed, as typed values are the same as previous')+'.', 'info')
            return redirect(url_for('librarians.account'))
    elif request.method == 'GET':
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.email.data = current_user.email
        form.phone.data = current_user.phone_print
        form.address.data = current_user.address
    return render_template('account_cu.html', form=form, admin_is_editing=False, is_creating=False)

@librarians.route("/account/password", methods=['GET', 'POST'])
@login_required
def account_password():
    form = LibrarianUpdatePasswordForm()
    if form.validate_on_submit():
        if bcrypt.check_password_hash(current_user.password, form.old_password.data):
            current_user.password = bcrypt.generate_password_hash(form.new_password.data).decode('utf-8')
            EventWriter.write(EventType.librarian_password, current_user.id, _g('Following librarian changed it\'s password')+' ('+_g('Librarian username')+': '+current_user.username+'):'+current_user.log_data())
            current_user.change_password = False
            db.session.commit()
            flash(_g('Account password is successfully updated')+'.', 'success')
            return redirect(url_for('librarians.account'))
        else:
            flash(_g('Current password value is not correct')+'.', 'error')
    return render_template('account_password_change.html', form=form)

@librarians.route("/librarians")
@login_required
def librarianss():
    if not current_user.is_admin:
        abort(403)
    include_inactive = request.args.get('include_inactive', 'False', type=str)
    sort_criteria = request.args.get('sort_by', 'first_name', type=str)
    sort_direction = request.args.get('direction', 'up', type=str)
    if not sort_criteria in sort_librarian_values:
        sort_criteria = 'first_name'

    include_disabled_val=True
    filter_args = {'include_inactive': 'True'}
    my_query = db.session.query(Librarian)
    if include_inactive == 'False':
        my_query = my_query.filter(Librarian.is_active)
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
    return render_template('account.html', account=librarian, admin_is_editing=True)

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
        db.session.flush()
        EventWriter.write(EventType.librarian_add, librarian.id, _g('Following librarian is added')+' ('+_g('Librarian username')+': '+librarian.username+'):'+librarian.log_data())
        db.session.commit()
        flash(_g('Account is successfully added')+'.', 'success')
        return redirect(url_for('librarians.librarianss'))
    return render_template('account_cu.html', form=form, is_creating=True)

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
        EventWriter.write(EventType.librarian_password_response, librarian.id, _g('Following librarian\'s password is changed on request')+' ('+_g('Librarian username')+': '+librarian.username+'):'+librarian.log_data())
        db.session.commit()
        flash(_g('Account password is successfully updated')+'.', 'success')
        return redirect(url_for('librarians.librarians_details', librarian_id=librarian.id))
    return render_template('account_password_change_request.html', form=form, librarian=librarian)

@librarians.route("/librarians/availability/<int:librarian_id>", methods=['GET', 'POST'])
@login_required
def librarians_availability(librarian_id):
    if not current_user.is_admin:
        abort(403)
    librarian = Librarian.query.get_or_404(librarian_id)
    if current_user.id == librarian_id:
        abort(405)
    form_decide = AcceptRejectForm()
    if not request.method == 'GET':
        if form_decide.reject.data and form_decide.validate():
            flash(_g('Account availability is not updated')+'.', 'info')
        elif form_decide.approve.data and form_decide.validate():
            librarian.is_active = not librarian.is_active
            if librarian.is_active:
                EventWriter.write(EventType.librarian_activate, librarian.id, _g('Following librarian\'s account is activated')+' ('+_g('Librarian username')+': '+librarian.username+'):'+librarian.log_data())
            else:
                EventWriter.write(EventType.librarian_deactivate, librarian.id, _g('Following librarian\'s account is deactivated')+' ('+_g('Librarian username')+': '+librarian.username+'):'+librarian.log_data())
            flash(_g('Account availability is successfully updated')+'.', 'info')
        db.session.commit()
        return redirect(url_for('librarians.librarianss'))
    return render_template('account_availability.html', form=form_decide, librarian=librarian)

@librarians.route("/librarians/administrate/<int:librarian_id>", methods=['GET', 'POST'])
@login_required
def librarians_administrate(librarian_id):
    if not current_user.is_admin:
        abort(403)
    librarian = Librarian.query.get_or_404(librarian_id)
    if not librarian.is_active:
        abort(405)
    if current_user.id == librarian_id: # da li admin menja sam sebe
        if not current_user.change_admin:   # ukoliko admin menja sebe, mora imati
            abort(405)                      # zahtev da treba prestati da bude admin
    elif librarian.change_admin:    # za ovog administratora vec postoji zahtev da se izbaci
        abort(405)

    form_decide = AcceptRejectForm()
    response = False
    success = False
    ch_regular_to_admin = False
    ch_admin_disable_req = False
    ch_admin_disable_resp = False
    msg_title = ''
    msg_approve = ''

    if not librarian.is_admin:  # treba da postane administrator
        ch_regular_to_admin = True
        msg_title = _g('Add librarian as administrator')
        msg_approve = _g('Please approve setting this librarian as the administrator')+'?'
    elif librarian.is_admin and not current_user.id == librarian_id: # trazimo da se iskljuci admin
        ch_admin_disable_req = True
        msg_title = _g('Librarian removal from administrators request')
        msg_approve = _g('Please approve your request to remove this librarian from administrators')+'.'
    elif librarian.is_admin and current_user.id == librarian_id and librarian.change_admin: # odlucuje da li ce prestati da bude admin
        ch_admin_disable_resp = True
        msg_title = _g('Your removal from administrators request')
        msg_approve = _g('Please approve or reject your removal from administrators')+'.'

    if request.method == 'GET':
        return render_template('account_administrate_request.html', form=form_decide, librarian=librarian, title=msg_title, text=msg_approve)
    elif request.method == 'POST':
        if form_decide.reject.data and form_decide.validate():
            response = False
            success = True
        elif form_decide.approve.data and form_decide.validate():
            response = True
            success = True
    if success:
        if ch_regular_to_admin and response:
            librarian.is_admin = True
            EventWriter.write(EventType.librarian_set_admin, librarian.id, _g('Following librarian\'s account is set as administrator')+' ('+_g('Librarian username')+': '+librarian.username+'):'+librarian.log_data())
            flash(_g('Librarian is successfully promoted to the administrator')+'.', 'info')
        elif ch_admin_disable_req and response:
            librarian.change_admin = True
            EventWriter.write(EventType.librarian_remove_admin_request, librarian.id, _g('Following librarian is requested to be removed from the administrators')+' ('+_g('Librarian username')+': '+librarian.username+'):'+librarian.log_data())
            flash(_g('You successfully created a request to remove librarian from the administrators')+'.', 'info')
        elif ch_admin_disable_resp and response:
            librarian.is_admin = False
            librarian.change_admin = False
            EventWriter.write(EventType.librarian_remove_admin_response, librarian.id, _g('Following librarian\'s request to be removed from administrators is approved')+' ('+_g('Librarian username')+': '+librarian.username+'):'+librarian.log_data())
            flash(_g('You are successfully removed from the administrators')+'.', 'info')
        elif ch_admin_disable_resp and not response:
            librarian.change_admin = False
            EventWriter.write(EventType.librarian_remove_admin_response, librarian.id, _g('Following librarian\'s request to be removed from administrators is rejected')+' ('+_g('Librarian username')+': '+librarian.username+'):'+librarian.log_data())
            flash(_g('You successfully rejected request to be removed from the administrators')+'.', 'info')
        db.session.commit()
    return redirect(url_for('librarians.librarianss'))

def has_new_values(user, form):
    return not (user.first_name == form.first_name.data and user.last_name == form.last_name.data and user.email == form.email.data and \
            user.phone == form.phone.data.replace("/", "") and user.address == form.address.data)
