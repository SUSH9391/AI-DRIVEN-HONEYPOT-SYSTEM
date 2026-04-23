import os
from flask import Flask, redirect, url_for
from flask_session import Session
from config import Config

# Blueprints
from routes.auth import auth_bp
from routes.dashboard import dashboard_bp
from routes.environments import environments_bp
from routes.sandbox import sandbox_bp
from routes.landing import landing_bp

def create_app(test_config=None):
    app = Flask(__name__, template_folder='templates', static_folder='static')
    app.config.from_object(Config)

    if test_config:
        app.config.update(test_config)

    # Initialize Flask-Session
    Session(app)

    # Register Blueprints
    app.register_blueprint(landing_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(environments_bp)
    app.register_blueprint(sandbox_bp)

    @app.before_request
    def check_valid_session():
        pass # Handle fine-grained within blueprints
        
    @app.template_filter('datetimeformat')
    def datetimeformat(value):
        from datetime import datetime
        if isinstance(value, str):
            try:
                # Handle Z at the end for ISO isoformat
                if value.endswith('Z'):
                    value = value[:-1]
                value = datetime.fromisoformat(value)
            except ValueError:
                return value
        if isinstance(value, datetime):
            return value.strftime('%b %d, %H:%M')
        return value

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=app.config.get('PORT', 5000))

