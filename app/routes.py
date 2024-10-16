from flask import render_template, flash, redirect, url_for
from app import app  
from app.forms import LoginForm

# this is called as view func: handlers for application routes.
# this decorator create an association b/w URL and the function. 
@app.route('/')
@app.route('/index')
def index():
	user = {'username' : 'shubham'}
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
	return render_template('index.html', title='Home', user=user,
							posts=posts)

@app.route('/login', methods=["GET", "POST"])
def login():
	form = LoginForm()
	 # validate_on_submit(): all the form processing work
	 # Return False for GET request
	 # Return: after gathering all the data and if it pass the validators
	if form.validate_on_submit():
		flash(f'Login requested for user {form.username.data}, remember_me={form.remember_me.data}')
		return redirect(url_for('index'))
	return render_template('login.html', title='Sign in', form=form)