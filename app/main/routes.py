from flask import (render_template, flash, redirect, 
 					url_for, request, g, current_app)
from app import db
from app.models import User, Post
from flask_login import (current_user,login_required)
from flask_babel import _, get_locale
import sqlalchemy as sa
from flask import request
from urllib.parse import urlsplit
from datetime import datetime, timezone
from app.main.forms import (EditProfileForm, EmptyForm, 
						PostForm)
from langdetect import detect, LangDetectException
from app.translate import translate
from app.main import bp
from flask import g
from app.main.forms import SearchForm

# this is called as view func: handlers for application routes.
# this decorator create an association b/w URL and the function. \
@bp.route('/', methods=['GET', 'POST'])
@bp.route('/index', methods=['GET', 'POST'])
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
		return redirect(url_for('main.index'))

	# adding pagination
	page = request.args.get('page', 1, type=int)
	posts = db.paginate(current_user.following_posts(), page=page,
					 per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
	# generating prev and next url for pagination
	next_url = url_for('main.index', page=posts.next_num) \
					if posts.has_next else None
	prev_url = url_for('main.index', page=posts.prev_num) \
					if posts.has_prev else None
	return render_template('index.html', title=_('Home Page'),
							posts=posts.items, form=form, 
							next_url=next_url, prev_url=prev_url)

@bp.route('/user/<username>') # only GET method
@login_required # only show this page if user is login
def user(username):
	"""View func to display user profile"""
	user = db.first_or_404(sa.select(User).where(User.username == username))
	page = request.args.get('page', 1, type=int)
	query = user.posts.select().order_by(Post.timestamp.desc())
	posts = db.paginate(query, page=page,
                        per_page=current_app.config['POSTS_PER_PAGE'],
                        error_out=False)
	next_url = url_for('main.user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
	prev_url = url_for('main.user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
	# for folow and unfollow 
	form = EmptyForm()
	return render_template('user.html', user=user, posts=posts.items, 
						form=form, next_url=next_url, prev_url=prev_url)



@bp.before_request
def before_request():
	""" 
	- func to run: with reach request. 
	- this func will be executed before any view function of the application. 
		to update last seen
	g: This g variable provided by Flask is a place where the application can 
	store data that needs to persist through the life of a request
	(this acts as a private storage for each request)
	"""
	if current_user.is_authenticated:
		# if the user in db then update last_seen column
		current_user.last_seen = datetime.now(timezone.utc)
		db.session.commit()
		g.search_form = SearchForm()
	g.locale = str(get_locale())

@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
	form = EditProfileForm(current_user.username)
	if form.validate_on_submit():
		current_user.username = form.username.data
		current_user.about_me = form.about_me.data
		db.session.commit()
		flash(_('Your Changes have been saved'))
		return redirect(url_for('main.edit_profile'))
	elif request.method == "GET":
		# getting the pre-populate data from current_user
		# instead from DB as it already loaded when 
		# a request been send to /user/<username> end point
		form.username.data = current_user.username
		form.about_me.data = current_user.about_me
	return render_template('edit_profile.html', title=_('Edit Profile'), 
						form=form)

@bp.route('/follow/<username>', methods=['POST'])
@login_required
def follow(username):
	form = EmptyForm()
	if form.validate_on_submit():
		user = db.session.scalar(
			sa.select(User).where(User.username == username))
		if user is None: 
			flash(_('User %(username)s not found.', username=username))
			return redirect(url_for('main.index'))
		if user == current_user:
			flash(_("You cannot follow yourself"))
			return redirect(url_for('main.user', username=username))
		current_user.follow(user)
		db.session.commit()
		flash(_('User %(username)s not found.', username=username))
		return redirect(url_for('main.user', username=username))
	else: 
		return redirect(url_for('main.index'))
	
@bp.route('/unfollow/<username>', methods=['POST'])
@login_required
def unfollow(username):
    form = EmptyForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == username))
        if user is None:
            flash(_('User %(username)s not found.', username=username))
            return redirect(url_for('main.index'))
        if user == current_user:
            flash(_('You cannot unfollow yourself!'))
            return redirect(url_for('main.user', username=username))
        current_user.unfollow(user)
        db.session.commit()
        flash(_('You are not following %(username)s.', username=username))
        return redirect(url_for('main.user', username=username))
    else:
        return redirect(url_for('main.index'))
	
@bp.route('/explore')
@login_required
def explore():
	"To display other User's Post on homepage"
	page = request.args.get('page', 1, type=int)
	query = sa.select(Post).order_by(Post.timestamp.desc())
	posts = db.paginate(query, page=page,
                        per_page=current_app.config['POSTS_PER_PAGE'], error_out=False)
	next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
	prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
	# Notice: render_template without the form.
	return render_template('index.html', title=_('Explore'),
						posts=posts.items,
						next_url=next_url, prev_url=prev_url)
	
@bp.route('/translate',  methods=['POST'])
@login_required
def translate_text():
	data = request.get_data()
	res = {'text': translate(data['text'], 
						  data['source_language'],
						  data['dest_language'])}

@bp.route('/search')
@login_required
def search():
	"To Handle GET request for elastic search"
	if not g.search_form.validate():
		return redirect(url_for('main.explore'))
	page = request.args.get('page', 1, type=int)
	posts, total = Post.search(g.search_form.q.data, page,
                               current_app.config['POSTS_PER_PAGE'])
	next_url = url_for('main.search', q=g.search_form.q.data, page=page + 1) \
        if total > page * current_app.config['POSTS_PER_PAGE'] else None
	prev_url = url_for('main.search', q=g.search_form.q.data, page=page - 1) \
        if page > 1 else None
	return render_template('search.html', title=_('Search'), posts=posts,
                           next_url=next_url, prev_url=prev_url)