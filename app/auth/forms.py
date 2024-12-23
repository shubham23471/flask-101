from flask_wtf import FlaskForm
# FlaskForm is the base Class
from wtforms import (StringField, PasswordField, 
					BooleanField, SubmitField)
from wtforms.validators import (DataRequired, ValidationError, 
                                Email, EqualTo)
from app.models import User
from app import db
import sqlalchemy as sa
from flask_babel import _, lazy_gettext as _l

class LoginForm(FlaskForm):
	username = StringField(_l('Username'), validators=[DataRequired()])
	password = PasswordField(_l('Password'), validators=[DataRequired()])
	remember_me = BooleanField(_l('Remember Me'))
	submit = SubmitField(_l('Sign In')) 

class RegistrationForm(FlaskForm):
	username = StringField(_l('Username'), validators=[DataRequired()])
	email = StringField(_l('Email'), validators=[DataRequired(), Email()])
	password = PasswordField(_l('Password'), validators=[DataRequired()])
	password2 = PasswordField(_l('Repeat Password'), validators=[DataRequired(), 
														  EqualTo('password')])
	submit = SubmitField(_l('Register'))

	# func suffix should be validate<field_name>
	# internally validates by Flask-WTF 
	def validate_username(self, username):
		# checking if user present in db
		user = db.session.scalar(sa.select(User).where(User.username == username.data))
		if user is not None: 
			raise ValidationError(_l('Username already taken!!. Please use a different username.'))

	def validate_email(self, email):
		user = db.session.scalar(sa.select(User).where(User.email == email.data))
		if user is not None: 
			raise ValidationError(_l('Please use a different email address'))

class ResetPasswordRequestForm(FlaskForm):
    email = StringField(_l('Email'), validators=[DataRequired(), Email()])
    submit = SubmitField(_l('Request Password Reset'))


class ResetPasswordForm(FlaskForm):
	password = PasswordField(_l('Password'), validators=[DataRequired()])
	password2 = PasswordField(_l('Repeat Password'), 
						   validators=[DataRequired(), EqualTo('password')])
	submit = SubmitField(_l('Request Password Reset'))