from flask import render_template
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
	return render_template('index.html', title='Home', user=user,
							posts=posts)

@app.route('/login')
def login():
	form = LoginForm()
	# title: the page title (shown on tab)
	return render_template('login.html', title='Sign in', form=form)