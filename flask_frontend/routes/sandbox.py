from flask import Blueprint, render_template, request, session, redirect, url_for, flash
import asyncio
from flask_frontend.services.fastapi_client import fastapi_client

sandbox_bp = Blueprint('sandbox', __name__, url_prefix='/sandbox')

@sandbox_bp.before_request
def require_auth():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

@sandbox_bp.route('/create', methods=['POST'])
def create():
    env_type = request.form.get('env_type')
    user_id = session.get('user_id')
    
    stats = asyncio.run(fastapi_client.get_user_stats(user_id))
    level = stats.get('level', 1)
    
    # Simple logic mapping user level to difficulty
    diff_map = {"sqli": 1, "xss": 2, "carding": 3, "path_traversal": 4}
    
    if diff_map.get(env_type, 1) > level + 1:
        flash("You need a higher level to enter this lab.", "warning")
        return redirect(url_for('environments.index'))
    
    resp = asyncio.run(fastapi_client.create_sandbox(user_id, env_type, difficulty_level=level))
    
    if 'error' in resp:
        flash("Failed to initialize sandbox.", "error")
        return redirect(url_for('environments.index'))
        
    session['active_sandbox'] = resp
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
    sandbox = session.get('active_sandbox')
    if not sandbox:
        return redirect(url_for('environments.index'))
        
    payload = request.form.to_dict()
    ip = request.remote_addr
    
    resp = asyncio.run(fastapi_client.score_attack(
        sandbox['sandbox_id'],
        sandbox['session_token'],
        payload,
        request.path,
        ip
    ))
    
    return render_template(sandbox['theme_template'], sandbox=sandbox, score=resp)

@sandbox_bp.route('/end', methods=['GET', 'DELETE'])
def end():
    sandbox = session.get('active_sandbox')
    if sandbox:
        asyncio.run(fastapi_client.end_sandbox(sandbox['sandbox_id']))
        session.pop('active_sandbox', None)
    return redirect(url_for('dashboard.index'))
