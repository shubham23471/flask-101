from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa 
import sqlalchemy.orm as so 
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login 
from hashlib import md5


# I am not declaring this table as a model, like I did for the users 
# and posts tables.
# auxiliary table that has no data other than the foreign keys
followers = sa.Table('followers', db.metadata, 
                    sa.Column('follower_id', sa.Integer, sa.ForeignKey('user.id'),
                                primary_key=True),
                    sa.Column('followed_id', sa.Integer, sa.ForeignKey('user.id'),
                                primary_key=True))

# use database model 
class User(UserMixin, db.Model):
    "Model class for user table"
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    username: so.Mapped[str] = so.mapped_column(sa.String(64), index=True,
                                                unique=True) 
    email: so.Mapped[str] = so.mapped_column(sa.String(120), index=True,
                                              unique=True)
    password_hash: so.Mapped[Optional[str]] = so.mapped_column(sa.String(256))
    
    # this is not a database field, but a high level view of relationship 
    # b/w user and post 
    posts: so.WriteOnlyMapped['Post'] = so.relationship(back_populates='author')
    about_me: so.Mapped[Optional[str]] = so.mapped_column(sa.String(140))
    last_seen: so.Mapped[Optional[datetime]] = so.mapped_column(
                                                default=lambda: datetime.now(timezone.utc))

    following: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers, primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        back_populates='followers')
    
    followers: so.WriteOnlyMapped['User'] = so.relationship(
        secondary=followers, primaryjoin=(followers.c.followed_id == id),
        secondaryjoin=(followers.c.follower_id == id),
        back_populates='following')

    def __repr__(self):
        return f'<User {self.username}>'
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def avatar(self, size):
        digest = md5(self.email.lower().encode('utf-8')).hexdigest()
        return f'https://www.gravatar.com/avatar/{digest}?d=identicon&s={size}'
    
    def is_following(self, user):
        "Check if user1 is following user2"
        query = self.following.select().where(User.id == user.id)
        return db.session.scalar(query) is not None
    
    def follow(self, user):
        """using write-only relationship object to add user 
        in following attribute of class User""" 
        if not self.is_following(user):
            self.following.add(user)
    
    def unfollow(self, user):
        if self.is_following(user):
            self.following.remove(user)
    


class Post(db.Model):
    "Model class for post table"
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, 
                                                      default=lambda: datetime.now(timezone.utc))

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

    author: so.Mapped[User] = so.relationship(back_populates='posts')

    def __repr__(self):
        return '<Post {}>'.format(self.body)

@login.user_loader  
def load_user(id):
    return db.session.get(User, int(id))