from datetime import datetime

from flask import Flask, render_template, request
from flask_login import LoginManager, login_required, login_user, logout_user, current_user, UserMixin
from flask_wtf import FlaskForm
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
from socket import gethostname
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)


def main():
    db.create_all()
    app.run(debug=True, host='0.0.0.0', port=80)


@app.route("/")
def index():
    return render_template("index.html")


@app.route('/<short_url>')
def redirect_to_url(short_url):
    link = db.session.query(Link).filter_by(short_url=short_url).first()

    link.visits = link.visits + 1
    db.session.commit()

    return redirect(link.original_url)


@app.route('/create_url')
@login_required
def create_url():
    return render_template('create_url.html', new_title='СОЗДАТЬ URL')


@app.route('/add_link', methods=['POST'])
@login_required
def add_link():
    original_url = request.form['original_url']
    short_url = request.form['new_path']
    if short_url in ['', 'create_url', 'add_link', 'stats', 'register', 'login', 'logout', 'profile'] or\
            original_url == '' or db.session.query(Link).filter(short_url == Link.short_url).first():
        return render_template('link_added_wrong.html', new_title='ОШИБКА')
    user_id = current_user.id
    link = Link(original_url=original_url, user_id=user_id, short_url=short_url)
    db.session.add(link)
    db.session.commit()

    return render_template('link_added.html', new_link=link.short_url, original_url=link.original_url,
                           new_title='ГОТОВО!', description='ТЕПЕРЬ ВЫ МОЖЕТЕ ПОЛЬЗОВАТЬСЯ НОВОЙ URL')


@app.route('/stats')
@login_required
def stats():
    links = db.session.query(Link).filter(current_user.id == Link.user_id)[::-1]

    return render_template('stats.html', links=links, new_title='ХРАНИЛИЩЕ')


@app.route('/delete_link', methods=['POST'])
@login_required
def delete_link():
    url_to_delete = request.form['url_to_delete']

    db.session.query(Link).filter(Link.id == url_to_delete).delete()
    db.session.commit()

    return render_template('delete_link.html', new_title='УСПЕШНО')


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    submit = SubmitField('Войти')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        if db.session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        if db.session.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с таким именем уже есть")
        user = User(name=form.name.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form, new_title='РЕГИСТРАЦИЯ')


@login_manager.user_loader
def load_user(user_id):
    return db.session.query(User).get(user_id)


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/create_url")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', new_title='АВТОРИЗАЦИЯ', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


class User(db.Model, UserMixin):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=True)
    email = db.Column(db.String, index=True, unique=True, nullable=True)
    hashed_password = db.Column(db.String, nullable=True)
    created_date = db.Column(db.DateTime, default=datetime.now)
    links = db.relationship('Link', backref='author', lazy=True)

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)


class Link(db.Model):

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    original_url = db.Column(db.String(512))
    short_url = db.Column(db.String(3))
    visits = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.now)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))


if __name__ == '__main__':
    main()
