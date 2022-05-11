from flask import Flask, render_template, flash
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
app = Flask(__name__)
app.config['SECRET_KEY'] ='helloworld'
class NameForm(FlaskForm):
    name = StringField("Please Enter your Name", validators=[DataRequired()])
    submit = SubmitField("Submit")
@app.route('/')
def index():
    return render_template('index.html')
# Invalid URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"),404
# Internal Server Error
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"),500
# ENter Name page
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
@app.route('/user/<name>')
def user(name):
    company=['Loid', 'Anya', 'Yor', 'Franky']
    return render_template('users.html', user_name=name, company=company)

if(__name__ == "__main__"):
    app.run(debug=True)
