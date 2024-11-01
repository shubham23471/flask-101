from datetime import datetime, timezone
from typing import Optional
import sqlalchemy as sa 
import sqlalchemy.orm as so 
from app import db, login
from werkzeug.security import (generate_password_hash, \
                               check_password_hash)
from flask_login import UserMixin
from app import login 
from hashlib import md5
from time import time 
from flask import current_app
import jwt
from app.search import (add_to_index, 
                        remove_from_index, 
                        query_index)


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
    
    def followers_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.followers.select().subquery())
        return db.session.scalar(query)

    def following_count(self):
        query = sa.select(sa.func.count()).select_from(
            self.following.select().subquery())
        return db.session.scalar(query)
    
    def following_posts(self):
        Author = so.aliased(User)
        Follower = so.aliased(User)
        return (
            sa.select(Post)
            .join(Post.author.of_type(Author))
            .join(Author.followers.of_type(Follower), isouter=True)
            .where(sa.or_(
                Follower.id == self.id,
                Author.id == self.id,
            ))
            .group_by(Post)
            .order_by(Post.timestamp.desc())
        )


    # def following_posts(self):
    #     return (
    #         Post.query
    #         .join(Post.author)
    #         .join(User.followers, isouter=True)
    #         .filter(
    #             sa.or_(
    #                 User.id == self.id,  # posts from users you follow
    #                 Post.author.id == self.id  # your own posts
    #             )
    #         )
    #         .group_by(Post)
    #         .order_by(Post.timestamp.desc())
    #     )

    # reset user password: token methods
    def get_reset_password_token(self, expires_in=600):
        res = jwt.encode({'reset_password': self.id, 
                   'exp': time() + expires_in},
                   current_app.config['SECRET_KEY'], algorithm='HS256')
        return res

    @staticmethod
    def verify_reset_password(token):
        try: 
            id =  jwt.decode(token, current_app.config['SECRET_KEY'],
                            algorithms=['HS256'])['reset_password']
        except:
            return
        return db.session.get(User, id)
    

@login.user_loader  
def load_user(id):
    return db.session.get(User, int(id))


class SearchableMixin(object):
    "To sync data b/w Elasaticsearch and SQLAlchemy"

    @classmethod
    def search(cls, expression, page, per_page): 
        ids, total = query_index(cls.__tablename__, expression,
                                 page, per_page)
        if total == 0: 
            return [], 0 
        when = []
        for i in range(len(ids)):
            when.append((ids[i], i))
        query = sa.select(cls).where(cls.id.in_(ids)).order_by(
            db.case(*when, value=cls.id))
        return db.sesion.scalars(query), total
    
    @classmethod
    def before_commit(cls, session):
        "To check the objects before SQLAlchemy trigger"
        session._changes = {
            'add' : list(session.new),
            'update': list(session.dirty),
            'delete': list(session.deleted )
            }
    
    @classmethod
    def after_commit(cls, session):
        for obj in session._changes['add']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['update']:
            if isinstance(obj, SearchableMixin):
                add_to_index(obj.__tablename__, obj)
        for obj in session._changes['delete']:
            if isinstance(obj, SearchableMixin):
                remove_from_index(obj.__tablename__, obj)
        session._changes = None
    
    @classmethod
    def reindex(cls): 
        "refresh all the data to refresh the index "
        for obj in db.session.scalars(sa.select(cls)):
            add_to_index(cls.__tablename__, obj)



class Post(SearchableMixin, db.Model):
    "Model class for post table"
    # attribute for searchable field for Elasticsearch
    __searchable__= ['body']
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    body: so.Mapped[str] = so.mapped_column(sa.String(140))
    timestamp: so.Mapped[datetime] = so.mapped_column(index=True, 
                                                      default=lambda: datetime.now(timezone.utc))

    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey(User.id), index=True)

    author: so.Mapped[User] = so.relationship(back_populates='posts')
    language: so.Mapped[Optional[str]] = so.mapped_column(sa.String(5))

    def __repr__(self):
        return '<Post {}>'.format(self.body)
    

db.event.listen(db.session, 'before_commit', SearchableMixin.before_commit)
db.event.listen(db.session, 'after_commit', SearchableMixin.after_commit)
