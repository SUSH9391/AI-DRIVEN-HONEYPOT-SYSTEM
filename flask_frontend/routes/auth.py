from flask import Blueprint, render_template, request, session, redirect, url_for, flash
import asyncio
from flask_frontend.services import fastapi_client as fc_module

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        result = asyncio.run(fc_module.fastapi_client.login_with_supabase(email, password))
        
        if result.get('error'):
            flash(result.get('detail', 'Login failed. Please try again.'), 'error')
            return render_template('auth/login.html'), 200  # <-- must be 200, not redirect
        
        session['user_id'] = result['user_id']
        session['username'] = result.get('username', 'user')
        session['jwt'] = result['jwt']
        session['level'] = result.get('level', 1)
        session['total_xp'] = result.get('total_xp', 0)
        return redirect(url_for('dashboard.index'))
        
    return render_template('auth/login.html')

@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        username = request.form.get('username')
        try:
            resp = asyncio.run(fc_module.fastapi_client.signup_with_supabase(email, password, username))
            if 'error' in resp:
                flash(resp['detail'], 'error')
            else:
                session['jwt'] = resp['jwt']
                session['user_id'] = resp['user_id']
                session['username'] = username
                return redirect(url_for('dashboard.index'))
        except Exception as e:
            flash("Signup failed", "error")
    return render_template('auth/signup.html')

@auth_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('landing.index'))
