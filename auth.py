from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from database import add_user, verify_user
import random
import string
from typing import Dict, Optional

auth_bp = Blueprint('auth', __name__)

def generate_password(length: int = 12, uppercase: bool = True, lowercase: bool = True, 
                    digits: bool = True, symbols: bool = True) -> str:
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

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        if not username or not password:
            flash('Имя пользователя и пароль обязательны', 'error')
            return render_template('register.html')
        
        if len(password) < 8:
            flash('Пароль должен содержать минимум 8 символов', 'error')
            return render_template('register.html')
        
        if not add_user(username, password):
            flash('Это имя пользователя уже занято', 'error')
            return render_template('register.html')
        
        flash('Регистрация прошла успешно! Теперь вы можете войти.', 'success')
        return redirect(url_for('auth.login'))
    
    generated_password = generate_password()
    return render_template('register.html', generated_password=generated_password)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        user = verify_user(username, password)
        
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Вы успешно вошли в систему', 'success')
            return redirect(url_for('index'))
        
        flash('Неверное имя пользователя или пароль', 'error')
    
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('Вы успешно вышли из системы', 'success')
    return redirect(url_for('auth.login'))