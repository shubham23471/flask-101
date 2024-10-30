from flask_wtf import FlaskForm
# FlaskForm is the base Class
from wtforms import (StringField,SubmitField, TextAreaField)
from wtforms.validators import (DataRequired, ValidationError, 
								Length)
from app.models import User
from app import db
import sqlalchemy as sa
from flask_babel import _, lazy_gettext as _l


class EditProfileForm(FlaskForm):
	username =  StringField(_l('Username'), validators=[DataRequired()]) 
	about_me = TextAreaField(_l('About me'), validators=[Length(min=0, max=140
														 )]) 
	submit = SubmitField(_l('Submit'))

	def __init__(self, original_username, *args , **kwargs):
		super().__init__(*args, **kwargs)
		self.original_username  = original_username

	def validate_username(self, username):
		if username.data != self.original_username:
			user = db.session.scalar(sa.select(User).where(
				User.username == username.data))
			if user is not None: 
				raise ValidationError(_l('Please use a different username'))
			

class EmptyForm(FlaskForm):
	"Empty form for follow and unfollow"
	submit = SubmitField(_l('Submit'))

class PostForm(FlaskForm):
	post = TextAreaField(_l('Say Something'), validators=[DataRequired(), 
												   Length(min=1, max=140)])
	submit = SubmitField(_l('Submit Post'))
