from flask import Flask, redirect, render_template, url_for, request, abort
from datetime import datetime, timedelta
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from sqlalchemy import ForeignKey, desc
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

# configs

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///database.db"
app.config['SECRET_KEY'] = ""

bcrypt = Bcrypt(app)
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

MAX_POST_AGE_IN_DAYS = 14

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
@login_required
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


@app.route("/dodawanie-zdjec/<int:news_id>", methods=['POST', 'GET'])
@login_required
def gallery_adding(news_id):
    if request.method == 'POST':
        gallery_photo = request.form['new-photo-link']
        gallery_photo_desc = request.form['new-photo-desc']

        new_photo = GalleryPhoto(photo_addres = gallery_photo, description = gallery_photo_desc, post_id = news_id)

        try:
            db.session.add(new_photo)
            db.session.commit()
            return redirect(request.url)
        except:
            return 'An error has occured!'

    else:
        photos = GalleryPhoto.query.filter(GalleryPhoto.post_id == news_id).all()
        current_post = Post.query.filter_by(id = news_id).first()
        return render_template("administration/gallery_adding.html", post = current_post, photos = photos)


@app.route('/delete-post/<int:id>')
@login_required
def delete_post(id):
    photos_to_delete = GalleryPhoto.query.filter(GalleryPhoto.post_id == id).all()
    post_to_delete = Post.query.get_or_404(id)
    try:
        for photo in photos_to_delete:
             db.session.delete(photo)
        db.session.commit()

        db.session.delete(post_to_delete)
        db.session.commit()
        return redirect(url_for('management'))
    except:
        return 'An error has occured!'


@app.route('/update-post/<int:id>', methods=['GET', 'POST'])
@login_required
def update_post(id):
    post = Post.query.get_or_404(id)

    if request.method == 'POST':
        post.title = request.form['title']
        post.main_photo = request.form['photo']
        post.content = request.form['content']

        try:
            db.session.commit()
            return redirect(url_for('management'))
        except:
            return 'An error has occured!'

    else:
        return render_template("administration/update_post.html", post = post)


@app.route('/publication-post/<int:id>')
@login_required
def update(id):
    post = Post.query.get_or_404(id)
    if post.is_public == 0:
        post.is_public = 1
    else:
        post.is_public = 0

    try:
        db.session.commit()
        return redirect(url_for('management'))
    except:
        return 'An error has occured!'


@app.route('/delete-photo/<int:id>')
@login_required
def delete_photo(id):
    photo_to_delete = GalleryPhoto.query.get_or_404(id)
    current_post = Post.query.get_or_404(photo_to_delete.post_id)
    try: 
        db.session.delete(photo_to_delete)
        db.session.commit()

        photos = GalleryPhoto.query.filter(GalleryPhoto.post_id == current_post.id).all()
        return render_template("administration/gallery_adding.html", post = current_post, photos = photos)
    except:
        return 'An error has occured!'


# main pages for average users

@app.route("/")
def home():
    filter_month = datetime.today() - timedelta(days = MAX_POST_AGE_IN_DAYS)
    three_posts = Post.query.filter(Post.is_public >= '1').filter(Post.date >= filter_month).order_by(desc(Post.date)).limit(3).all()
    return render_template("home.html", posts = three_posts)

@app.route("/o-parafii")
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
    post = Post.query.get_or_404(id)
    if post.is_public < 1:
        abort(404)

    filter_month = datetime.today() - timedelta(days = MAX_POST_AGE_IN_DAYS)
    three_posts = Post.query.filter(Post.is_public >= '1').filter(Post.id != id).filter(Post.date >= filter_month).order_by(desc(Post.date)).limit(3).all()
    photos = GalleryPhoto.query.filter(GalleryPhoto.post_id == id).all()
    return render_template("single_news.html", post = post, posts = three_posts, photos = photos)


# church subpages

@app.route("/o-parafii/historia-parafii")
def history():
    return render_template("church-subpages/history.html")

@app.route("/o-parafii/architektura")
def architecture():
    return render_template("church-subpages/architecture.html")

@app.route("/o-parafii/zabytki")
def monuments():
    return render_template("church-subpages/monuments.html")

@app.route("/o-parafii/proboszczowie")
def priests():
    return render_template("church-subpages/priests.html")

@app.route("/o-parafii/zywoty-swiatych")
def saints():
    return render_template("church-subpages/saints.html")

@app.route("/o-parafii/ruchoma-szopka")
def xmas():
    return render_template("church-subpages/xmas.html")


@app.route("/o-parafii/kapliczki-przydrozne")
def chapels():
    return render_template("church-subpages/chapels.html")


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

@app.route("/wspolnoty/rada-parafialna")
def council():
    return render_template("groups-subpages/council.html")


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


@app.errorhandler(404)
def page_not_found(e):
    return render_template('error/404.html'), 404


if __name__ == "__main__":
    app.run(debug=True)

