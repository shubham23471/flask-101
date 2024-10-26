from flask_wtf import FlaskForm
# FlaskForm is the base Class
from wtforms import (StringField, PasswordField, 
					BooleanField, SubmitField, TextAreaField)
from wtforms.validators import (DataRequired, ValidationError, 
                                Email, EqualTo, Length)
from app.models import User
from app import db
import sqlalchemy as sa

class LoginForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	password = PasswordField('Password', validators=[DataRequired()])
	remember_me = BooleanField('Remember Me')
	submit = SubmitField('Sign In') 

class RegistrationForm(FlaskForm):
	username = StringField('Username', validators=[DataRequired()])
	email = StringField('Email', validators=[DataRequired(), Email()])
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField('Repeat Password', validators=[DataRequired(), 
														  EqualTo('password')])
	submit = SubmitField('Register')

	# func suffix should be validate<field_name>
	# internally validates by Flask-WTF 
	def validate_username(self, username):
		# checking if user present in db
		user = db.session.scalar(sa.select(User).where(User.username == username.data))
		if user is not None: 
			raise ValidationError('Username already taken!!. Please use a different username.')

	def validate_email(self, email):
		user = db.session.scalar(sa.select(User).where(User.email == email.data))
		if user is not None: 
			raise ValidationError('Please use a different email address')


class EditProfileForm(FlaskForm):
	username =  StringField('Username', validators=[DataRequired()]) 
	about_me = TextAreaField('About me', validators=[Length(min=0, max=140
														 )]) 
	submit = SubmitField('Submit')

	def __init__(self, original_username, *args , **kwargs):
		super().__init__(*args, **kwargs)
		self.original_username  = original_username

	def validate_username(self, username):
		if username.data != self.original_username:
			user = db.session.scalar(sa.select(User).where(
				User.username == username.data))
			if user is not None: 
				raise ValidationError('Please use a different username')
			

class EmptyForm(FlaskForm):
	"Empty form for follow and unfllow"
	submit = SubmitField('Submit')

class PostForm(FlaskForm):
	post = TextAreaField('Say Something', validators=[DataRequired(), 
												   Length(min=1, max=140)])
	submit = SubmitField('Submit Post')


class ResetPasswordRequestForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Request Password Reset')


class ResetPasswordForm(FlaskForm):
	password = PasswordField('Password', validators=[DataRequired()])
	password2 = PasswordField('Repeat Password', 
						   validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField('Request Password Reset')