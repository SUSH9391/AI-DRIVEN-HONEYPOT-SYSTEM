from flask import Blueprint, render_template, session, redirect, url_for
import asyncio
from flask_frontend.services import fastapi_client as fc_module

environments_bp = Blueprint('environments', __name__, url_prefix='/environments')

@environments_bp.before_request
def require_auth():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

@environments_bp.route('/')
def index():
    user_id = session.get('user_id')
    stats = asyncio.run(fc_module.fastapi_client.get_user_stats(
        user_id,
        jwt=session.get('jwt')
    ))
    level = stats.get('level', 1)
    
    envs = [
        {"id": "sqli", "name": "SQL Injection Lab", "desc": "Bypass banking and corporate portals via SQLi.", "difficulty": 1, "unlocked": level >= 1},
        {"id": "xss", "name": "Cross-Site Scripting Lab", "desc": "Exploit social feeds and forums with XSS.", "difficulty": 2, "unlocked": level >= 1},
        {"id": "carding", "name": "Carding Fraud Lab", "desc": "Test e-commerce platforms with fake carding bots.", "difficulty": 3, "unlocked": level >= 2},
        {"id": "path_traversal", "name": "Path Traversal Lab", "desc": "Access sensitive files from a server panel.", "difficulty": 4, "unlocked": level >= 3}
    ]
    
    return render_template('environments.html', environments=envs, user_level=level)
