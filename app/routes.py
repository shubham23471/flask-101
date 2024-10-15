from flask import render_template
from app import app  

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