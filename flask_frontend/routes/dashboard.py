from flask import Blueprint, render_template, session, redirect, url_for
import asyncio
from flask_frontend.services.fastapi_client import fastapi_client

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.before_request
def require_auth():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

@dashboard_bp.route('/')
def index():
    user_id = session.get('user_id')
    stats = asyncio.run(fastapi_client.get_user_stats(user_id))
    
    if 'error' in stats:
        stats = {"total_xp": 0, "level": 1, "badges": [], "attack_history": [], "leaderboard_rank": 0}
        
    # Calculate progress % (mock calculation based on levels described)
    xp = stats.get('total_xp', 0)
    level = stats.get('level', 1)
    
    thresholds = [0, 200, 500, 1000, 2000, 3000, 4000, 5000]
    next_level_xp = thresholds[level] if level < len(thresholds) else thresholds[-1]
    prev_level_xp = thresholds[level-1] if level > 0 else 0
    
    pct = 100
    if next_level_xp > prev_level_xp:
        pct = min(100, int(((xp - prev_level_xp) / (next_level_xp - prev_level_xp)) * 100))

    return render_template('dashboard.html', 
                           username=session.get('username'),
                           stats=stats,
                           progress_pct=pct)
