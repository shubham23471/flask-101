from flask import (render_template, flash, redirect, 
 					url_for, request, g)
from app import app, db
from app.forms import LoginForm, RegistrationForm
from app.models import User, Post
from flask_login import (current_user, login_user, 
						logout_user, login_required)
from flask_babel import _, get_locale
import sqlalchemy as sa
from flask import request
from urllib.parse import urlsplit
from datetime import datetime, timezone
from app.forms import (EditProfileForm, EmptyForm, 
						PostForm, ResetPasswordRequestForm,
						ResetPasswordForm)
from app.email import send_password_reset_email
from langdetect import detect, LangDetectException
from app.translate import translate

# this is called as view func: handlers for application routes.
# this decorator create an association b/w URL and the function. \
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
	form = PostForm()
	if form.validate_on_submit():
		try: 
			language = detect(form.post.data)
		except LangDetectException:
			language = ''
		post = Post(body=form.post.data, author=current_user, 
			  		language=language)
		post = Post(body=form.post.data, author=current_user)
		db.session.add(post)
		db.session.commit()
		flash(_('Your post is now live!'))
		# Because it is a standard practice to always
		# respond to a POST request generated by a web form submission with a redirect
		# This simple trick is called the Post/Redirect/Get pattern.
		return redirect(url_for('index'))

	# adding pagination
	page = request.args.get('page', 1, type=int)
	posts = db.paginate(current_user.following_posts(), page=page,
					 per_page=app.config['POSTS_PER_PAGE'], error_out=False)
	# generating prev and next url for pagination
	next_url = url_for('index', page=posts.next_num) \
					if posts.has_next else None
	prev_url = url_for('index', page=posts.prev_num) \
					if posts.has_prev else None
	return render_template('index.html', title=_('Home Page'),
							posts=posts.items, form=form, 
							next_url=next_url, prev_url=prev_url)

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
			flash(_('Invalid Username or password'))
			return redirect(url_for('login'))
		login_user(user=user, remember=form.remember_me.data)
		# redirecting the user to "next" page after login
		next_page = request.args.get('next')
		print(f'requests: {request}')
		print(f'next_page: {next_page}')
		if not next_page or urlsplit(next_page).netloc != '':
			next_page = url_for('index')
		return redirect(next_page)
	return render_template('login.html', title=_('Sign in'), form=form)


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
		flash(_('Congratulations, you are now a registered user!'))
		return redirect(url_for('login'))
	return render_template('register.html', title=_('Register'), form=form)

@app.route('/user/<username>') # only GET method
@login_required # only show this page if user is login
def user(username):
	"""View func to display user profile"""
	user = db.first_or_404(sa.select(User).where(User.username == username))
	page = request.args.get('page', 1, type=int)
	query = user.posts.select().order_by(Post.timestamp.desc())
	posts = db.paginate(query, page=page,
                        per_page=app.config['POSTS_PER_PAGE'],
                        error_out=False)
	next_url = url_for('user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
	prev_url = url_for('user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
	# for folow and unfollow 
	form = EmptyForm()
	return render_template('user.html', user=user, posts=posts.items, 
						form=form, next_url=next_url, prev_url=prev_url)



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
	g.locale = str(get_locale())

@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm(current_user.username)
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.about_me = form.about_me.data
		db.session.commit()
		flash(_('Your Changes have been saved'))
		return redirect(url_for('edit_profile'))
	elif request.method == "GET":
		# getting the pre-populate data from current_user
		# instead from DB as it already loaded when 
		# a request been send to /user/<username> end point
		form.username.data = current_user.username
		form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', title=_('Edit Profile'), 
						form=form)

@app.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
	form = EmptyForm()
	if form.validate_on_submit():
		user = db.session.scalar(
			sa.select(User).where(User.username == username))
		if user is None: 
			flash(_('User %(username)s not found.', username=username))
			return redirect(url_for('index'))
		if user == current_user:
			flash(_("You cannot follow yourself"))
			return redirect(url_for('user', username=username))
		current_user.follow(user)
		db.session.commit()
		flash(_('User %(username)s not found.', username=username))
		return redirect(url_for('user', username=username))
	else: 
		return redirect(url_for('index'))
	
@app.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('index'))
        if user == current_user:
            flash(_('You cannot unfollow yourself!'))
            return redirect(url_for('user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_('You are not following %(username)s.', username=username))
        return redirect(url_for('user', username=username))
    else:
        return redirect(url_for('index'))
	
@app.route('/explore')
@login_required
def explore():
	"To display other User's Post on homepage"
	page = request.args.get('page', 1, type=int)
	query = sa.select(Post).order_by(Post.timestamp.desc())
	posts = db.paginate(query, page=page,
                        per_page=app.config['POSTS_PER_PAGE'], error_out=False)
	next_url = url_for('explore', page=posts.next_num) \
        if posts.has_next else None
	prev_url = url_for('explore', page=posts.prev_num) \
        if posts.has_prev else None
	# Notice: render_template without the form.
	return render_template('index.html', title=_('Explore'),
						posts=posts.items,
						next_url=next_url, prev_url=prev_url)


@app.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
	"Sending password reset email "
	if current_user.is_authenticated: 
		return redirect(url_for('index'))

	form = ResetPasswordRequestForm()
	if form.validate_on_submit():
		user = db.session.scalar(
			sa.select(User).where(User.email == form.email.data)
				)
		if user: 
			send_password_reset_email(user)
		flash(_('Check your email for the intructions to reset your password'))
		return redirect(url_for('login'))
	return render_template('reset_password_request.html',
                           title=_('Reset Password'), form=form)


@app.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
	"Reset User password"
	if current_user.is_authenticated: 
		return redirect(url_for('index'))
	# verify token and get user id
	user = User.verify_reset_password(token)
	if not user: 
		return redirect(url_for('index'))
	form = ResetPasswordForm()
	if form.validate_on_submit():
		user.set_password(form.password.data)
		db.sesion.commit()
		flash(_('Your Password has been reset'))
		return redirect(url_for('login'))
	return render_template('reset_password.html', form=form)

	
@app.route('/translate',  methods=['POST'])
@login_required
def translate_text():
	data = request.get_data()
	res = {'text': translate(data['text'], 
						  data['source_language'],
						  data['dest_language'])}