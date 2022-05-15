from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import yaml
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)

# Add Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:password@localhost/blog'
# DATABSE intialsiation
data = yaml.full_load(open('data.yaml'))
app.config['SECRET_KEY'] = data['secret_key']
# app.config['MYSQL_HOST'] = data['mysql_host']
# app.config['MYSQL_USER'] = data['mysql_user']
# app.config['MYSQL_PASSWORD'] = data['mysql_password']
# app.config['MYSQL_DB'] = data['mysql_db']
# mysql = MySQL(app)

db = SQLAlchemy(app)
migrate = Migrate(app, db)


# Creating Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=True, unique=True)
    favourite_anime = db.Column(db.String(200))
    password_hash = db.Column(db.String(128), nullable=False)
    date_added = db.Column(db.DateTime)
    @property
    def password(self):
        raise AttributeError('password is not valid')
    @password.setter
    def password(self, password):
        self.password_hash=generate_password_hash(password)
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)


#     Creating a String
def __repr__(self):
    return '<Name %r>' % self.name


class NameForm(FlaskForm):
    name = StringField("Please Enter your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")


class UserProfile(FlaskForm):
    name = StringField("Please Enter your Name", validators=[DataRequired()])
    email = StringField("Please Enter your Email", validators=[DataRequired()])
    favourite_anime = StringField("Please enter the name of your favourite anime")
    submit = SubmitField("Submit")


@app.route('/')
def index():
    return render_template('index.html')


# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# Internal Server Error
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


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
def update(id):
    form = UserProfile()
    name_to_update = Users.query.get_or_404(id)
    if request.method == 'POST':
        name_to_update.name = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favourite_anime = request.form['favourite_anime']
        try:
            db.session.commit()
            flash("User updated sucessfully")
            return render_template('update.html', form=form, name_to_update=name_to_update)
        except:
            flash("Error! please try again")
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
            user = Users(name=form.name.data, email=form.email.data, favourite_anime=form.favourite_anime.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.favourite_anime.data
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

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
