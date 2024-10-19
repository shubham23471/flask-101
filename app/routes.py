from flask import render_template, flash, redirect, url_for
from app import app, db
from app.forms import LoginForm
from app.models import User
from flask_login import (current_user, login_user, 
						logout_user, login_required)
import sqlalchemy as sa
from flask import request
from urllib.parse import urlsplit

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