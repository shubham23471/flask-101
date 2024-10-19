from flask import render_template, flash, redirect, url_for
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User
from flask_login import (current_user, login_user, 
						logout_user, login_required)
import sqlalchemy as sa
from flask import request
from urllib.parse import urlsplit
from datetime import datetime, timezone
from app.forms import EditProfileForm

# this is called as view func: handlers for application routes.
# this decorator create an association b/w URL and the function. 
@app.route('/')
@app.route('/index')
@login_required
def index():
	posts = [{
            'author': {'username': 'John'},
            'body': 'Beautiful day in Portland!'
        },
        {
            'author': {'username': 'Susan'},
            'body': 'The Avengers movie was so cool!'
        }
    ]
	# title: the page title (shown on tab)
	return render_template('index.html', title='Home',
							posts=posts)

@app.route('/login', methods=["GET", "POST"])
def login():
	if current_user.is_authenticated: 
		return redirect(url_for('index'))
	form = LoginForm()
	 # validate_on_submit(): all the form processing work
	 # Return False for GET request
	 # Return: after gathering all the data and if it pass the validators
	if form.validate_on_submit():
		user = db.session.scalar(
			sa.select(User).where(User.username == form.username.data))
		if user is None or not user.check_password(form.password.data):
			flash('Invalid Username or password')
			return redirect(url_for('login'))
		login_user(user=user, remember=form.remember_me.data)
		# redirecting the user to "next" page after login
		next_page = request.args.get('next')
		print(f'requests: {request}')
		print(f'next_page: {next_page}')
		if not next_page or urlsplit(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page)
	return render_template('login.html', title='Sign in', form=form)


@app.route('/logout')
def logout():
	logout_user()
	return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
	""" Redirect the user to /register, validates the data and add it to db"""
	if current_user.is_authenticated:
		# show the home/index page
		return redirect(url_for('index'))

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
		flash('Congratulations, you are now a registered user!')
		return redirect(url_for('login'))
	return render_template('register.html', title='Register', form=form)

@app.route('/user/<username>') # only GET method
@login_required # only show this page if user is login
def user(username):
	"""View func to display user profile"""
	user = db.first_or_404(sa.select(User).where(User.username == username))
	posts = [
		{'author': user, 'body' : "Test post 1"},
		{'author': user, 'body': 'Test post #2'}
	]
	return render_template('user.html', user=user, posts=posts)



@app.before_request
def before_request():
	""" 
	- func to run: with reach request. 
	- this func will be executed before any view function of the application. 
	
	to update last seen"""
	if current_user.is_authenticated:
		# if the user in db then update last_seen column
		current_user.last_seen = datetime.now(timezone.utc)
		db.session.commit()

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm(current_user.username)
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.about_me = form.about_me.data
		db.session.commit()
		flash('Your Changes have been saved')
		return redirect(url_for('edit_profile'))
	elif request.method == "GET":
		# getting the pre-populate data from current_user
		# instead from DB as it already loaded when 
		# a request been send to /user/<username> end point
		form.username.data = current_user.username
		form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', title='Edit Profile', 
						form=form)