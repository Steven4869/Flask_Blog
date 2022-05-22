from flask import Flask, render_template, flash, request, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError, TextAreaField
from flask_wtf.file import FileField
from wtforms.validators import DataRequired, EqualTo, Length
import yaml
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_ckeditor import CKEditor, CKEditorField
from werkzeug.utils import secure_filename
import uuid as uuid
import os
from datetime import datetime
from datetime import date

app = Flask(__name__)
app.config['CKEDITOR_PKG_TYPE'] = 'standard'
ckeditor = CKEditor(app)

# DATABSE intialsiation
data = yaml.full_load(open('data.yaml'))
app.config['SECRET_KEY'] = data['secret_key']
# Add Database
app.config['SQLALCHEMY_DATABASE_URI'] = data['database_uri']
db = SQLAlchemy(app)
migrate = Migrate(app, db)

UPLOAD_FOLDER ='static/images/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Flask Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


# Creating a Blog Post Model
class Posts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text())
    # author = db.Column(db.String(255), nullable=False)
    date_posted = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(255))
    # Create a foreign key to link users(primary key fo users model
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))


# Creating Post Form
class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    # content = CKEditorField("Content", validators=[DataRequired()])
    content = CKEditorField("Content")
    author = StringField("Author")
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit ")


# Creating Model
class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), nullable=False, unique=True)
    name = db.Column(db.String(200), nullable=False)
    about_author = db.Column(db.Text(500), nullable=True)
    email = db.Column(db.String(200), nullable=True, unique=True)
    favourite_anime = db.Column(db.String(200))
    profile_pic = db.Column(db.String(500), nullable=True)
    password_hash = db.Column(db.String(128), nullable=False)
    date_added = db.Column(db.DateTime, default=datetime.utcnow)
    posts = db.relationship('Posts', backref='poster')

    @property
    def password(self):
        raise AttributeError('password is not valid')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


#     Creating a String
def __repr__(self):
    return '<Name %r>' % self.name


class NameForm(FlaskForm):
    name = CKEditorField("Please Enter your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")


class UserProfile(FlaskForm):
    name = StringField("Please Enter your Name", validators=[DataRequired()])
    username = StringField("Please enter your username", validators=[DataRequired()])
    email = StringField("Please Enter your Email", validators=[DataRequired()])
    favourite_anime = StringField("Please enter the name of your favourite anime")
    about_author = TextAreaField("Give details about the author(optional")
    profile_pic = FileField("Profile Picture")
    password_hash = PasswordField("password", validators=[DataRequired(),
                                                          EqualTo('password_hash2', message="Passwords must match")])
    password_hash2 = PasswordField("Confirm Password", validators=[DataRequired()])
    submit = SubmitField("Submit")


class LoginForm(FlaskForm):
    username = StringField("Please enter your username", validators=[DataRequired()])
    password = PasswordField("Please enter your Password", validators=[DataRequired()])
    submit = SubmitField("submit")


class SearchForm(FlaskForm):
    searched = StringField("Searched", validators=[DataRequired()])
    submit = SubmitField("submit")


@app.route('/')
def index():
    return render_template('index.html')


# Passing parameters to navbar
@app.context_processor
def base():
    form = SearchForm()
    return dict(form=form)

# Search Function
@app.route('/search', methods=['POST'])
def search():
    form = SearchForm()
    posts = Posts.query
    if form.validate_on_submit():
        post.searched = form.searched.data
        posts = posts.filter(Posts.content.like('%' + post.searched + '%'))
        posts = posts.order_by(Posts.title).all()
        return render_template('search.html', form=form, searched=post.searched, posts=posts)

# Admin Page
@app.route('/admin')
@login_required
def admin():
    username = current_user.username
    if username == 'Shivam728':
        return render_template('admin.html')
    else:
        flash("You don't have access to Admin Page ")
        return redirect(url_for('dashboard'))
# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# Internal Server Error
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


# Add Post Page
@app.route('/add-post', methods=['GET', 'POST'])
# To show the page only when user is logged in
@login_required
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        poster = current_user.id
        post = Posts(title=form.title.data, content=form.content.data, author_id=poster, slug=form.slug.data)
        form.title.data = ''
        form.content.data = ''
        form.slug.data = ''
        # Add post to the database
        db.session.add(post)
        db.session.commit()

        flash("Post submitted successfully")

    return render_template("add_post.html", form=form)


# Show the Posts Page
@app.route('/posts')
def posts():
    # Taking blog posts from database
    posts = Posts.query.order_by(Posts.date_posted.desc())
    return render_template('posts.html', posts=posts)


# Separate page for the blog
@app.route('/posts/<int:id>')
def post(id):
    post = Posts.query.get_or_404(id)
    return render_template('post.html', post=post)


# Editing Posts
@app.route('/posts/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_posts(id):
    post = Posts.query.get_or_404(id)
    form = PostForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        post.slug = form.slug.data

        db.session.add(post)
        db.session.commit()
        flash("Post has been updated")

        return redirect(url_for('post', id=post.id))
    if current_user.id == post.author_id:
        form.title.data = post.title
        form.slug.data = post.slug
        form.content.data = post.content
        return render_template('edit_posts.html', form=form)
    else:
        flash("Access Denied ")
        posts = Posts.query.order_by(Posts.date_posted)
        return render_template('posts.html', posts=posts)


# Deleting Blog Posts
@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Posts.query.get_or_404(id)
    id = current_user.id
    if id == post_to_delete.poster.id:
        try:
            db.session.delete(post_to_delete)
            db.session.commit()
            flash("Post Deleted successfully")
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template('posts.html', posts=posts)
        except:
            flash("There's problem deleting the post, Please try again")
            posts = Posts.query.order_by(Posts.date_posted)
            return render_template('posts.html', posts=posts)


# Login Page
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                flash("Login successfully")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong password, Try Again")
        else:
            flash("User doesn't exist, Please fill it properly")
    return render_template('login.html', form=form)


# Logout function
@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("Logged out")
    return redirect(url_for('login'))


# Dashboard Page
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    return render_template('dashboard.html')


# Enter Name page
@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None;
    form = NameForm()
    # Validating the form
    # Pass the data to name if the form validates on submit
    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("From submitted successfully")

    return render_template('name.html', name=name, form=form)


# Updating users name and email
@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    form = UserProfile()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favourite_anime = request.form['favourite_anime']
        name_to_update.about_author = request.form['about_author']

        if request.files['profile_pic']:
            name_to_update.profile_pic = request.files['profile_pic']
            pic_filename = secure_filename(name_to_update.profile_pic.filename)
            pic_name = str(uuid.uuid1()) + "_" + pic_filename
            saver = request.files['profile_pic']
            name_to_update.profile_pic = pic_name
            try:
                db.session.commit()
                saver.save(os.path.join(app.config['UPLOAD_FOLDER'], pic_name))
                flash("User updated sucessfully")
                return render_template('update.html', form=form, name_to_update=name_to_update)
            except:
                flash("Error! please try again")
                return render_template('update.html', form=form, name_to_update=name_to_update)
        else:
            db.session.commit()
            flash("User updated sucessfully")
            return render_template('update.html', form=form, name_to_update=name_to_update)

    else:
        return render_template('update.html', form=form, name_to_update=name_to_update)


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None;
    form = UserProfile()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            # Hashing the password
            hashed_password = generate_password_hash(form.password_hash.data, "sha256")
            user = Users(username=form.username.data, name=form.name.data, email=form.email.data,
                         favourite_anime=form.favourite_anime.data,about_author=form.about_author.data,
                         password_hash=hashed_password)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.username.data = ''
        form.email.data = ''
        form.favourite_anime.data = ''
        form.about_author.data = ''
        form.password_hash.data = ''
        flash("User Added Successfully")
    display_users = Users.query.order_by(Users.date_added)
    return render_template('add_user.html', form=form, name=name, display_users=display_users)


# Deleting an record
@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = Users.query.get_or_404(id)
    name = None;
    form = UserProfile()
    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted successfully")
        display_users = Users.query.order_by(Users.date_added)
        return render_template('add_user.html', form=form, name=name, display_users=display_users)
    except:
        flash("There's problem deleting the user, Please try again")
        return render_template('add_user.html', form=form, name=name, display_users=display_users)


@app.route('/user/<name>')
def user(name):
    company = ['Loid', 'Anya', 'Yor', 'Franky']
    return render_template('users.html', user_name=name, company=company)


if (__name__ == "__main__"):
    app.run(debug=True)

