from flask import (render_template, flash, redirect, 
 					url_for, request, g)
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User
from flask_login import (current_user, login_user, 
						logout_user)
from flask_babel import _
import sqlalchemy as sa
from flask import request
from urllib.parse import urlsplit
from app.forms import (ResetPasswordRequestForm,
						ResetPasswordForm)
from app.email import send_password_reset_email
from app.auth import bp

@bp.route('/login', methods=["GET", "POST"])
def login():
	if current_user.is_authenticated: 
		return redirect(url_for('main.index'))
	form = LoginForm()
	 # validate_on_submit(): all the form processing work
	 # Return False for GET request
	 # Return: after gathering all the data and if it pass the validators
	if form.validate_on_submit():
		user = db.session.scalar(
			sa.select(User).where(User.username == form.username.data))
		if user is None or not user.check_password(form.password.data):
			flash(_('Invalid Username or password'))
			return redirect(url_for('auth.login'))
		login_user(user=user, remember=form.remember_me.data)
		# redirecting the user to "next" page after login
		next_page = request.args.get('next')
		print(f'requests: {request}')
		print(f'next_page: {next_page}')
		if not next_page or urlsplit(next_page).netloc != '':
			next_page = url_for('main.index')
		return redirect(next_page)
	return render_template('login.html', title=_('Sign in'), form=form)


@bp.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('main.index'))

@bp.route('/register', methods=['GET', 'POST'])
def register():
	""" Redirect the user to /register, validates the data and add it to db"""
	if current_user.is_authenticated:
		# show the home/index page
		return redirect(url_for('main.index'))

	# get user data on submit
	form = RegistrationForm()
	if form.validate_on_submit():
		# runs all the validation func by Flask-WTF 
		# along with the custom validate_<field_name>
		user = User(username=form.username.data, 
			  		email=form.email.data)
		user.set_password(form.password.data)
		db.session.add(user)
		db.session.commit()
		flash(_('Congratulations, you are now a registered user!'))
		return redirect(url_for('auth.login'))
	return render_template('register.html', title=_('Register'), form=form)

@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
	"Sending password reset email "
	if current_user.is_authenticated: 
		return redirect(url_for('main.index'))

	form = ResetPasswordRequestForm()
	if form.validate_on_submit():
		user = db.session.scalar(
			sa.select(User).where(User.email == form.email.data)
				)
		if user: 
			send_password_reset_email(user)
		flash(_('Check your email for the intructions to reset your password'))
		return redirect(url_for('auth.login'))
	return render_template('reset_password_request.html',
                           title=_('Reset Password'), form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
	"Reset User password"
	if current_user.is_authenticated: 
		return redirect(url_for('main.index'))
	# verify token and get user id
	user = User.verify_reset_password(token)
	if not user: 
		return redirect(url_for('main.index'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		user.set_password(form.password.data)
		db.sesion.commit()
		flash(_('Your Password has been reset'))
		return redirect(url_for('auth.login'))
	return render_template('reset_password.html', form=form)