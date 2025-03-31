from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from database import init_db, close_db, get_db, query_db, add_password, get_passwords, update_password, delete_password
from auth import auth_bp
import os
import random
import string

app = Flask(__name__)
app.secret_key = os.urandom(24)
app.register_blueprint(auth_bp)

init_db(app)

app.teardown_appcontext(close_db)

def generate_password(length=12, uppercase=True, lowercase=True, digits=True, symbols=True):
    characters = ''
    if uppercase:
        characters += string.ascii_uppercase
    if lowercase:
        characters += string.ascii_lowercase
    if digits:
        characters += string.digits
    if symbols:
        characters += '!@#$%^&*()_+-=[]{}|;:,.<>?'
    
    if not characters:
        characters = string.ascii_letters + string.digits
    
    return ''.join(random.choice(characters) for _ in range(length))

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
        length = int(request.form.get('length', 12))
        uppercase = 'uppercase' in request.form
        lowercase = 'lowercase' in request.form
        digits = 'digits' in request.form
        symbols = 'symbols' in request.form
        
        password = generate_password(length, uppercase, lowercase, digits, symbols)
        return render_template('generate.html', password=password)
    
    return render_template('generate.html')

@app.route('/manage', methods=['GET', 'POST'])
def manage():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            name = request.form.get('name')
            password = request.form.get('password')
            if name and password:
                add_password(session['user_id'], name, password)
                flash('Пароль успешно добавлен', 'success')
        elif action == 'update':
            password_id = request.form.get('id')
            new_password = request.form.get('new_password')
            if password_id and new_password:
                password_id = int(password_id)
                if update_password(password_id, new_password):
                    flash('Пароль успешно обновлен', 'success')
        elif action == 'delete':
            password_id = request.form.get('id')
            if password_id:
                password_id = int(password_id)  
                if delete_password(password_id):
                    flash('Пароль успешно удален', 'success')
    
    passwords = get_passwords(session['user_id'])
    return render_template('manage.html', passwords=passwords)

if __name__ == '__main__':
    app.run(debug=True)
