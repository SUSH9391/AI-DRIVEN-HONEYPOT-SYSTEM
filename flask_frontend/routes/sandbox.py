from flask import Blueprint, render_template, request, session, redirect, url_for, flash
import asyncio
from flask_frontend.services import fastapi_client as fc_module

sandbox_bp = Blueprint('sandbox', __name__, url_prefix='/sandbox')

@sandbox_bp.before_request
def require_auth():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

@sandbox_bp.route('/create', methods=['POST'])
def create():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    env_type = request.form.get('env_type')
    difficulty = session.get('level', 1)
    
    # Simple logic mapping user level to difficulty
    diff_map = {"sqli": 1, "xss": 2, "carding": 3, "path_traversal": 4}
    
    if diff_map.get(env_type, 1) > difficulty + 1:
        flash("You need a higher level to enter this lab.", "warning")
        return redirect(url_for('environments.index'))
    
    result = asyncio.run(
        fc_module.fastapi_client.create_sandbox(
            session['user_id'], env_type, difficulty
        )
    )
    
    if not result or result.get('error'):
        flash('Could not create sandbox. Please try again.', 'error')
        return redirect(url_for('environments.index'))
    
    session['active_sandbox'] = {
        'sandbox_id': result['sandbox_id'],
        'session_token': result.get('session_token', ''),
        'theme_template': result['theme_template'],
        'env_type': env_type,
    }
    return redirect(url_for('sandbox.play'))

@sandbox_bp.route('/play')
def play():
    sandbox = session.get('active_sandbox')
    if not sandbox:
        return redirect(url_for('environments.index'))
        
    theme = sandbox.get('theme_template')
    return render_template(theme, sandbox=sandbox)

@sandbox_bp.route('/attack', methods=['POST'])
def attack():
    active_sandbox = session.get('active_sandbox')
    if not active_sandbox:
        return redirect(url_for('environments.index'))
    
    payload = dict(request.form)
    
    result = asyncio.run(
        fc_module.fastapi_client.score_attack(
            sandbox_id=active_sandbox['sandbox_id'],
            session_token=active_sandbox['session_token'],
            attack_payload=payload,
            attack_surface=active_sandbox.get('theme_template', ''),
            source_ip=request.remote_addr or '127.0.0.1'
        )
    )
    
    if result.get('level_up'):
        flash(f"Level Up! You reached Level {result.get('level')}!", 'level_up')
    
    theme = active_sandbox.get('theme_template', 'sqli/banking_login.html')
    return render_template(
        theme,
        score=result,
        attack_detected=result.get('attack_detected', False),
        show_overlay=True
    )

@sandbox_bp.route('/end', methods=['GET', 'DELETE'])
def end():
    sandbox = session.get('active_sandbox')
    if sandbox:
        asyncio.run(fc_module.fastapi_client.end_sandbox(sandbox['sandbox_id']))
        session.pop('active_sandbox', None)
    return redirect(url_for('dashboard.index'))
