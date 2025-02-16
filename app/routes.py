import os
from app import db
import logging
from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app, jsonify
from flask_login import login_user, logout_user, login_required, current_user
# 注意：这里移除了 from app import db
from app.models import User, Post, Comment
from app.forms import RegisterForm, LoginForm, PostForm, CommentForm
import markdown

# 创建 Blueprint
main = Blueprint('main', __name__)

logging.basicConfig(filename='my_app.log',
                    level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

@main.route('/')
def index():
    # return render_template('index.html')
    posts = Post.query.order_by(Post.date_posted.desc()).limit(3).all()  # ✅ 获取所有文章，按时间倒序
    for post in posts:
        post.date_posted_readable = format_date(post.date_posted)
    return render_template('index.html', posts=posts)

def format_date(date):
    if date:
        return date.strftime('%b %d, %Y %H:%M:%S')  # 自定义日期格式
    return ''

@main.route('/load_more_posts', methods=['GET'])
def load_more_posts():


    # 获取请求参数，例如 offset 和 limit，用于分页
    offset = request.args.get('offset', type=int, default=0)
    limit = request.args.get('limit', type=int, default=10)  # 默认每页10篇文章

    # 查询更多文章，这里使用了 offset 和 limit 进行分页
    more_posts = Post.query.order_by(Post.date_posted.desc()).offset(offset).limit(limit).all()

    # 将文章数据转换为 JSON 格式
    post_list = []
    for post in more_posts:
        post_data = {
            'title': post.title,  # 假设你的 Post 模型有 title 属性
            'date_posted': post.date_posted.strftime('%Y-%m-%d %H:%M:%S'), # 格式化日期时间
            # ... 其他需要的文章属性
        }
        post_list.append(post_data)

    return jsonify(post_list)


# @main.route('/register', methods=['GET', 'POST'])
# def register():
#     # from app import db  # 将 from app import db 移动到函数内部
#     form = RegisterForm()
#     if form.validate_on_submit():
#         existing_user = User.query.filter_by(username=form.username.data).first()
#         if existing_user:
#             flash('用户名已存在，请选择其他用户名', 'danger')
#             return redirect(url_for('main.register'))
#
#         new_user = User(username=form.username.data, password=form.password.data)
#         db.session.add(new_user)
#         db.session.commit()
#
#         flash('注册成功！请登录。', 'success')
#         return redirect(url_for('main.login'))
#
#     return render_template('register.html', form=form)

@main.route('/static/<int:post_id>')
def post(post_id):
    post = Post.query.get_or_404(post_id)
    logging.debug(post.author.username)
    post.date_posted = format_date(post.date_posted)
    logging.debug(post.date_posted)
    return render_template('post.html', post=post)


@main.route('/post_total', methods=['GET', 'POST'])
@login_required  # ✅ 只有登录用户可以发布文章
def post_total():
    posts = Post.query.order_by(Post.date_posted.desc()).all()  # ✅ 获取所有文章，按时间倒序
    return render_template('post_total.html', posts=posts)

# 创建新文章
@main.route('/new_post', methods=['GET', 'POST'])
@login_required  # ✅ 只有登录用户可以发布文章
def new_post():
    form = PostForm()
    if form.validate_on_submit():
        new_post = Post(
            title=form.title.data,
            content=form.content.data,
            user_id=current_user.id  # ✅ 关联当前用户
        )
        db.session.add(new_post)
        db.session.commit()
        flash('文章发布成功！', 'success')
        return redirect(url_for('main.index'))  # ✅ 跳转到首页

    return render_template('new_post.html', form=form)

# @main.route('/new_post', methods=['GET', 'POST'])
# @login_required
# def new_post():
#     form = PostForm()
#     if form.validate_on_submit():
#         try:
#             content_markdown = form.content.data
#             content_html = markdown.markdown(content_markdown)
#         except Exception as e:
#             flash(f'Markdown 转换失败：{e}', 'danger')
#             return render_template('new_post.html', form=form)
#
#         new_post = Post(
#             title=form.title.data,
#             content=content_html,  # 只存储 HTML 内容
#             user_id=current_user.id
#         )
#         db.session.add(new_post)
#         db.session.commit()
#         flash('文章发布成功！', 'success')
#         return redirect(url_for('main.index'))
#
#     return render_template('new_post.html', form=form)



@main.route('/delete_post/<int:post_id>', methods=['POST'])
@login_required  # ✅ 只有登录用户可以删除
def delete_post(post_id):
    post = Post.query.get_or_404(post_id)  # ✅ 确保文章存在
    if post.author.id != current_user.id:
        flash('你没有权限删除这篇文章', 'danger')
        return redirect(url_for('main.index'))

    db.session.delete(post)
    db.session.commit()
    flash('文章已删除', 'success')
    return redirect(url_for('main.index'))


@main.route('/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required  # ✅ 只有登录用户可以修改
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)  # ✅ 找到文章
    if post.author.id != current_user.id:
        flash('你没有权限编辑这篇文章', 'danger')
        return redirect(url_for('main.index'))

    form = PostForm()
    if request.method == 'GET':  # ✅ 预填充表单
        form.title.data = post.title
        form.content.data = post.content

    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()  # ✅ 提交修改
        flash('文章已更新！', 'success')
        return redirect(url_for('main.index'))

    return render_template('edit_post.html', form=form, post=post)


@main.route('/post/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)  # ✅ 获取博客文章
    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.date_posted.desc()).all()
    form = CommentForm()

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('请先登录再发表评论', 'danger')
            return redirect(url_for('main.login'))

        new_comment = Comment(content=form.content.data, user_id=current_user.id, post_id=post.id)
        db.session.add(new_comment)
        db.session.commit()
        flash('评论成功！', 'success')
        return redirect(url_for('main.post_detail', post_id=post.id))

    return render_template('post_detail.html', post=post, comments=comments, form=form)



@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('you have logout', 'info')
    return redirect(url_for('main.login'))

@main.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            flash('login successful！', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('username or password error', 'danger')

    return render_template('login.html', form=form)

@main.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(username=form.username.data).first()
        if existing_user:
            flash('username exist, select other username', 'danger')
            return redirect(url_for('main.register'))

        new_user = User(username=form.username.data, password=form.password.data)
        db.session.add(new_user)
        db.session.commit()

        flash('register successful! login please', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html', form=form)

@main.route('/dashboard')
@login_required
def dashboard():
    return "这是一个受限页面，只有登录用户可以看到！"

# ... 其他路由 ...