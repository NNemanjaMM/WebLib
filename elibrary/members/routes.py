from datetime import date, timedelta
from flask import render_template, url_for, redirect, request, flash, Blueprint, abort
from flask_login import current_user, login_required
from flask_babel import gettext, lazy_gettext as _l
from elibrary import db
from elibrary.models import Member
from elibrary.members.forms import MemberCreateForm, MemberUpdateForm, UserExtensionForm
from elibrary.utils.numeric_defines import MEMBERSHIP_EXTENSION_DAYS
from elibrary.main.forms import AcceptForm, RejectForm

members = Blueprint('members', __name__)

@members.route("/members/all")
@login_required
def members_all():
    list = Member.query.order_by('first_name').all()

    return render_template('members.html', members_list=list, include_expired=True)
@members.route("/members/active")
@login_required
def members_active():
    list = Member.query.filter(Member.date_expiration >= date.today()).order_by('first_name').all()
    return render_template('members.html', members_list=list, include_expired=False)

@members.route("/members/details/<int:member_id>")
@login_required
def members_details(member_id):
    member = Member.query.get_or_404(member_id)
    return render_template('member.html', member=member)


@members.route("/members/create", methods=['GET', 'POST'])
@login_required
def members_create():
    form = MemberCreateForm()
    if form.validate_on_submit():
        member = Member()
        member.first_name = form.first_name.data
        member.last_name = form.last_name.data
        member.birth_date = form.birth_date.data
        member.email = form.email.data
        member.phone_1 = form.phone_1.data
        member.phone_2 = form.phone_2.data
        member.address = form.address.data
        member.town = form.town.data
        member.date_registered = form.date_registered.data
        member.date_expiration = form.date_registered.data + timedelta(MEMBERSHIP_EXTENSION_DAYS)
        db.session.add(member)
        db.session.commit()
        flash(_l('New member has been added')+'.', 'success')
        return redirect(url_for('members.members_all'))
    return render_template('member_create.html', form=form, is_creating=True)

@members.route("/members/update/<int:member_id>", methods=['GET', 'POST'])
@login_required
def members_update(member_id):
    member = Member.query.get_or_404(member_id)

    form = MemberUpdateForm()
    if form.validate_on_submit():
        member.first_name = form.first_name.data
        member.last_name = form.last_name.data
        member.birth_date = form.birth_date.data
        member.email = form.email.data
        member.phone_1 = form.phone_1.data
        member.phone_2 = form.phone_2.data
        member.address = form.address.data
        member.town = form.town.data
        db.session.commit()
        flash(_l('Member data has been updated')+'.', 'success')
        return redirect(url_for('members.members_details',member_id=member.id))
    elif request.method == 'GET':
        form.first_name.data = member.first_name
        form.last_name.data = member.last_name
        form.birth_date.data = member.birth_date
        form.email.data = member.email
        form.phone_1.data = member.phone_1
        form.phone_2.data = member.phone_2
        form.address.data = member.address
        form.town.data = member.town
    return render_template('member_create.html', form=form, is_creating=False)

@members.route("/members/extend/<int:member_id>", methods=['GET', 'POST'])
@login_required
def members_extend(member_id):
    member = Member.query.get_or_404(member_id)
    if not member.is_membership_near_expired:
        abort(405)

    form = UserExtensionForm()
    if member.is_membership_expired:
        new_date_expiration = date.today() + timedelta(MEMBERSHIP_EXTENSION_DAYS)
    else:
        new_date_expiration = member.date_expiration + timedelta(MEMBERSHIP_EXTENSION_DAYS)
        form.fixed_value = True
    form.maximum_date = new_date_expiration

    if form.validate_on_submit():
        member.date_expiration = form.extension_date.data
        flash(_l('Member\'s membership is extended for')+' '+str(MEMBERSHIP_EXTENSION_DAYS)+' '+_l('days')+'.', 'info')
        db.session.commit()
        return redirect(url_for('members.members_details', member_id=member.id))

    form.extension_date.data = new_date_expiration
    return render_template('member_extension.html', form=form, member=member, expiration_proposal=new_date_expiration)
