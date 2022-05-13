from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import yaml
from flask_sqlalchemy import SQLAlchemy
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


# Creating Model
class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=True, unique=True)
    date_added = db.Column(db.DateTime)


#     Creating a String
def __repr__(self):
    return '<Name %r>' % self.name


class NameForm(FlaskForm):
    name = StringField("Please Enter your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")


class UserProfile(FlaskForm):
    name = StringField("Please Enter your Name", validators=[DataRequired()])
    email = StringField("Please Enter your Email", validators=[DataRequired()])
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


@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    name = None;
    form = UserProfile()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user is None:
            user = Users(name=form.name.data, email=form.email.data)
            db.session.add(user)
            db.session.commit()
        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        flash("User Added Successfully")
    display_users = Users.query.order_by(Users.date_added)
    return render_template('add_user.html', form=form, name=name, display_users=display_users)


@app.route('/user/<name>')
def user(name):
    company = ['Loid', 'Anya', 'Yor', 'Franky']
    return render_template('users.html', user_name=name, company=company)


if (__name__ == "__main__"):
    app.run(debug=True)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
