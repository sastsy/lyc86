from flask import Flask, render_template, request
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from flask_wtf import FlaskForm
from werkzeug.utils import redirect
from wtforms import PasswordField, StringField, TextAreaField, SubmitField, BooleanField
from wtforms.fields.html5 import EmailField
from wtforms.validators import DataRequired
import sqlalchemy

from data import db_session
from data.users import User
from data.link import Link

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


def main():
    db_session.global_init("db/blogs.sqlite")
    app.run(debug=True, host='0.0.0.0', port=80)


login_manager = LoginManager()
login_manager.init_app(app)


@app.route("/")
def index():
    session = db_session.create_session()
    # news = session.query(News).filter(News.is_private != True)
    return render_template("index.html")


@app.route('/<short_url>')
def redirect_to_url(short_url):
    session = db_session.create_session()
    link = session.query(Link).filter_by(short_url=short_url).first()

    link.visits = link.visits + 1
    session.commit()

    return redirect(link.original_url)


@app.route('/create_url')
@login_required
def create_url():
    return render_template('create_url.html', new_title='СОЗДАТЬ URL')


@app.route('/add_link', methods=['POST'])
@login_required
def add_link():
    session = db_session.create_session()
    original_url = request.form['original_url']
    short_url = request.form['new_path']
    if short_url in ['', 'create_url', 'add_link', 'stats', 'register', 'login', 'logout', 'profile'] or\
            original_url == '' or session.query(Link).filter(short_url == Link.short_url).first():
        return render_template('link_added_wrong.html', new_title='ОШИБКА')
    user_id = current_user.id
    link = Link(original_url=original_url, user_id=user_id, short_url=short_url)
    session.add(link)
    session.commit()

    return render_template('link_added.html', new_link=link.short_url, original_url=link.original_url,
                           new_title='ГОТОВО!', description='ТЕПЕРЬ ВЫ МОЖЕТЕ ПОЛЬЗОВАТЬСЯ НОВОЙ URL')


@app.route('/stats')
@login_required
def stats():
    session = db_session.create_session()

    links = session.query(Link).filter(current_user.id == Link.user_id)[::-1]

    return render_template('stats.html', links=links, new_title='ХРАНИЛИЩЕ')


@app.route('/delete_link', methods=['POST'])
@login_required
def delete_link():
    session = db_session.create_session()
    url_to_delete = request.form['url_to_delete']

    session.query(Link).filter(Link.id == url_to_delete).delete()
    session.commit()

    return render_template('delete_link.html', new_title='УСПЕШНО')


class RegisterForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    about = TextAreaField("Немного о себе")
    submit = SubmitField('Войти')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        session = db_session.create_session()
        if session.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        if session.query(User).filter(User.name == form.name.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пользователь с таким именем уже есть")
        user = User(name=form.name.data, email=form.email.data, about=form.about.data)
        user.set_password(form.password.data)
        session.add(user)
        session.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form, new_title='РЕГИСТРАЦИЯ')


@login_manager.user_loader
def load_user(user_id):
    session = db_session.create_session()
    return session.query(User).get(user_id)


class LoginForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        session = db_session.create_session()
        user = session.query(User).filter(User.email == form.email.data).first()
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


if __name__ == '__main__':
    main()