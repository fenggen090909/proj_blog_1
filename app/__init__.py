from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from config import Config
import os




# 初始化 Flask
app = Flask(__name__, template_folder=os.path.abspath('templates'))
app.config.from_object(Config)

# 初始化数据库
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# 初始化 Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'main.login'  # 这里使用 Blueprint

from app.models import User

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))  # ✅ 让 Flask-Login 可以加载用户

# **导入并注册 Blueprint**
from app.routes import main  # 确保 routes 在 app 初始化后导入
app.register_blueprint(main)
