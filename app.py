from flask import Flask, render_template, request, redirect, url_for, session, flash
import random
import string
from database import init_db, add_password, get_passwords, update_password, delete_password
from auth import auth_bp

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.register_blueprint(auth_bp)

@app.before_request
def initialize_database():
    if 'db_initialized' not in session:
        init_db()
        session['db_initialized'] = True


def generate_password(length=12):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    return render_template('index.html')

@app.route('/generate', methods=['GET', 'POST'])
def generate():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        length = int(request.form['length'])
        password = generate_password(length)
        return render_template('generate.html', password=password)
    return render_template('generate.html')

@app.route('/manage', methods=['GET', 'POST'])
def manage():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        action = request.form['action']
        if action == 'add':
            name = request.form['name']
            password = request.form['password']
            add_password(session['user_id'], name, password)
        elif action == 'update':
            id = request.form['id']
            new_password = request.form['new_password']
            update_password(id, new_password)
        elif action == 'delete':
            id = request.form['id']
            delete_password(id)
    passwords = get_passwords(session['user_id'])
    return render_template('manage.html', passwords=passwords)

if __name__ == '__main__':
    app.run(debug=True)
