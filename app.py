from flask import Flask, redirect, render_template, url_for, request
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from sqlalchemy import ForeignKey, desc
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

# configs

app = Flask(__name__)
bcrypt = Bcrypt(app)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SECRET_KEY'] = "parafiasw"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# database models

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)
    is_admin = db.Column(db.Integer, default=0)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    main_photo = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    content = db.Column(db.String(3000), nullable=False)
    is_public = db.Column(db.Integer, default=0)


class GalleryPhoto(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, ForeignKey(Post.id))
    photo_addres = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(200), nullable=True)


# registration and login forms

class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Nazwa użytkownika"})
    password1 = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Hasło"})
    password2 = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Powtórzenie hasła"})
    submit = SubmitField('Zarejestruj')

    def validate_username(self, username):
        existing_user_username = User.query.filter_by(username = username.data).first()
        if existing_user_username:
            raise ValidationError('Username already exists.')


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)], render_kw={"placeholder": "Nazwa użytkownika"})
    password = PasswordField(validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Hasło"})
    submit = SubmitField('Zaloguj')


# administration pages

@app.route("/admin")
def admin():
    return render_template("administration/admin.html")


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('management'))

    return render_template("administration/login.html", form = form)


@app.route("/registration", methods=['GET', 'POST'])
def registration():
    form = RegisterForm()

    if form.validate_on_submit():
        if form.password1.data == form.password2.data:
            hashed_password = bcrypt.generate_password_hash(form.password1.data)
            new_user = User(username=form.username.data, password=hashed_password, is_admin = 1)
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))

        else: return redirect(url_for('registration'))

    return render_template("administration/registration.html", form = form)


@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/management")
@login_required
def management():
    posts = Post.query.order_by(desc(Post.date)).all()
    return render_template("administration/post_management.html", posts = posts)


@app.route("/nowy", methods=['POST', 'GET'])
@login_required
def nowy():
    if request.method == 'POST':
        post_title = request.form['title']
        post_photo = request.form['photo']
        post_content = request.form['content']

        new_post = Post(title = post_title, main_photo = post_photo, content = post_content, is_public = 1)

        try:
            db.session.add(new_post)
            db.session.commit()
            return redirect(url_for('management'))
        except:
            return 'An error has occured!'

    else:
        return render_template("administration/new_post.html")


# main pages for average users

@app.route("/")
def home():
    three_posts = Post.query.filter(Post.is_public >= '1').order_by(desc(Post.date)).limit(3).all()
    return render_template("home.html", posts = three_posts)

@app.route("/swiatynia")
def church():
    return render_template("church.html")

@app.route("/aktualnosci")
def news():
    posts = Post.query.filter(Post.is_public >= '1').order_by(desc(Post.date)).limit(9).all()
    return render_template("news.html", posts = posts)

@app.route("/wspolnoty")
def groups():
    return render_template("groups.html")

@app.route("/kancelaria")
def office():
    return render_template("office.html")

@app.route("/kontakt")
def contact():
    return render_template("contact.html")

@app.route("/aktualnosci/<int:id>")
def single_news(id):
    post = Post.query.filter_by(id = id).first()
    three_posts = Post.query.filter(Post.is_public >= '1').filter(Post.id != id).order_by(desc(Post.date)).limit(3).all()
    return render_template("single_news.html", post = post, posts = three_posts)


# church subpages

@app.route("/swiatynia/historia-parafii")
def history():
    return render_template("church-subpages/history.html")

@app.route("/swiatynia/architektura")
def architecture():
    return render_template("church-subpages/architecture.html")

@app.route("/swiatynia/zabytki")
def monuments():
    return render_template("church-subpages/monuments.html")

@app.route("/swiatynia/proboszczowie")
def priests():
    return render_template("church-subpages/priests.html")

@app.route("/swiatynia/zywoty-swiatych")
def saints():
    return render_template("church-subpages/saints.html")

@app.route("/swiatynia/ruchoma-szopka")
def xmas():
    return render_template("church-subpages/xmas.html")

# groups subpages

@app.route("/wspolnoty/liturgiczna-sluzba-oltarza")
def lso():
    return render_template("groups-subpages/lso.html")

@app.route("/wspolnoty/dziewczeca-sluzba-maryjna")
def dsm():
    return render_template("groups-subpages/dsm.html")

@app.route("/wspolnoty/grupa-apostolska")
def ga():
    return render_template("groups-subpages/ga.html")

@app.route("/wspolnoty/caritas")
def caritas():
    return render_template("groups-subpages/caritas.html")


#office subpages
@app.route("/kancelaria/chrzest")
def baptism():
    return render_template("office-subpages/baptism.html")

@app.route("/kancelaria/malzenstwo")
def marriage():
    return render_template("office-subpages/marriage.html")

@app.route("/kancelaria/bierzmowanie")
def confirmation():
    return render_template("office-subpages/confirmation.html")

@app.route("/kancelaria/pierwsza-komunia")
def communion():
    return render_template("office-subpages/communion.html")

@app.route("/kancelaria/spowiedz")
def confession():
    return render_template("office-subpages/confession.html")

@app.route("/kancelaria/namaszczenie-chorych")
def illness():
    return render_template("office-subpages/illness.html")

@app.route("/kancelaria/pogrzeb")
def funeral():
    return render_template("office-subpages/funeral.html")


if __name__ == "__main__":
    app.run(debug=True)

