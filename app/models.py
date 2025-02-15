from datetime import datetime
from app import db
from flask_login import UserMixin

# 用户表
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 关联用户
    author = db.relationship('User', backref=db.backref('posts', lazy=True))  # ✅ 反向引用

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # 关联用户
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)  # 关联博客文章

    author = db.relationship('User', backref=db.backref('comments', lazy=True))  # 让评论获取作者
    post = db.relationship('Post', backref=db.backref('comments', lazy=True))  # 让文章获取评论
