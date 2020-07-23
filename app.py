from flask import Flask, render_template, abort, redirect, url_for, flash

from flask_login import UserMixin, LoginManager, login_user, logout_user, current_user, login_required

from flask_sqlalchemy import SQLAlchemy

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField,PasswordField
from wtforms import validators

import click
from datetime import datetime

app = Flask(__name__)

app.secret_key = '21321321332rdsnfpowhfcznxsahpdcbabcs'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////{}/data.db'.format(
    app.root_path)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)

# 创建用户加载回调函数，接受用户 ID 作为参数
# 用 ID 作为 User 模型的主键查询对应的用户


@login_manager.user_loader
def load_user(user_id):
    user = User.query.get(int(user_id))
    return user


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    password = db.Column(db.String(80))
    regtime = db.Column(db.DateTime())


class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    data = db.Column(db.String())


@app.cli.command()
def initdb():
    db.drop_all()
    db.create_all()
    user = User(username='root', password='123456', regtime=datetime.now())
    db.session.add(user)
    db.session.commit()


login_manager.login_view = 'login'


@app.route('/', methods=['get', 'post'])
@login_required
def index():
    return render_template('starter.html')

class Loginform(FlaskForm):
    username = StringField('用户', [validators.required()])
    password = PasswordField('密码', [validators.required()])
    submit = SubmitField('登录')

@app.route('/login', methods=['get', 'post'])
def login():
    form = Loginform()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            flash('login success')
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('login failed=>'+form.username.data)
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/login')
