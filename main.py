from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def hello():
    return render_template('index.html')

@app.route('/user/<name>')
def user(name):
    company=['Loid', 'Anya', 'Yor', 'Franky']
    return render_template('users.html', user_name=name, company=company)

if(__name__ == "__main__"):
    app.run(debug=True)
