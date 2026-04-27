from flask import Blueprint, render_template, session, redirect, url_for
import asyncio
from flask_frontend.services import fastapi_client as fc_module

dashboard_bp = Blueprint('dashboard', __name__, url_prefix='/dashboard')

@dashboard_bp.before_request
def require_auth():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

@dashboard_bp.route('/')
def index():
    user_id = session.get('user_id')
    stats = asyncio.run(fc_module.fastapi_client.get_user_stats(
        user_id,
        jwt=session.get('jwt')
    ))
    
    # Check if get_user_stats succeeded; if not use mock data structure
    if 'error' in stats:
        stats = {"total_xp": session.get('total_xp', 0), "level": session.get('level', 1), "badges": [], "attack_history": [], "leaderboard_rank": 0}
    else:
        # Keep session up to date
        session['total_xp'] = stats.get('total_xp', 0)
        session['level'] = stats.get('level', 1)
        session.modified = True
        
    try:
        leaderboard = asyncio.run(fc_module.fastapi_client.get_leaderboard())
    except Exception:
        leaderboard = []

    ALL_BADGES = [
        {"id": "first_blood", "name": "First Blood", "icon": "🩸", "desc": "First detection"},
        {"id": "sql_slinger", "name": "SQL Slinger", "icon": "💉", "desc": "5 SQLi detections"},
        {"id": "script_kiddie", "name": "Script Kiddie", "icon": "📜", "desc": "5 XSS detections"},
        {"id": "card_shark", "name": "Card Shark", "icon": "💳", "desc": "3 carding detections"},
        {"id": "ghost_walker", "name": "Ghost Walker", "icon": "👻", "desc": "3 path traversal detections"},
        {"id": "streak", "name": "On a Streak", "icon": "🔥", "desc": "3 detections in one session"},
    ]
        
    # Calculate progress %
    xp = stats.get('total_xp', 0)
    level_num = stats.get('level', 1)
    
    thresholds = [0, 200, 500, 1000, 2000, 3000, 4000, 5000]
    next_level_xp = thresholds[level_num] if level_num < len(thresholds) else thresholds[-1]
    prev_level_xp = thresholds[level_num-1] if level_num > 0 else 0
    
    level_progress_pct = 100
    if next_level_xp > prev_level_xp:
        level_progress_pct = max(0, min(100, int(((xp - prev_level_xp) / (next_level_xp - prev_level_xp)) * 100)))

    return render_template('dashboard.html', 
                           username=session.get('username'),
                           stats=stats,
                           total_xp=xp,
                           level=level_num,
                           level_progress_pct=level_progress_pct,
                           xp_for_next_level=next_level_xp,
                           recent_attacks=stats.get('attack_history', []),
                           leaderboard=leaderboard,
                           all_badges=ALL_BADGES,
                           earned_badge_ids=stats.get('badges', []),
                           current_user_id=user_id)
