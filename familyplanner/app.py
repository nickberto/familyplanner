"""
Application factory and initialization.
"""
from flask import Flask
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from familyplanner.config import get_config
from familyplanner.models import db, User


def create_app(config=None) -> Flask:
    """
    Create and configure the Flask application.
    
    Args:
        config: Configuration object. If None, uses environment-based config.
    
    Returns:
        Configured Flask application instance.
    """
    app = Flask(__name__)
    
    # Load configuration
    if config is None:
        config = get_config()
    app.config.from_object(config)
    
    # Initialize extensions
    db.init_app(app)
    
    csrf = CSRFProtect()
    csrf.init_app(app)
    
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Bitte melden Sie sich an, um auf diese Seite zuzugreifen."
    
    @login_manager.user_loader
    def load_user(user_id):
        """Load user by ID for session management."""
        return User.query.get(int(user_id))
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    # Register blueprints
    from familyplanner.web import auth, calendar
    app.register_blueprint(auth.bp)
    app.register_blueprint(calendar.bp)
    
    # Security headers
    @app.after_request
    def set_security_headers(response):
        """Add security headers to all responses."""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "SAMEORIGIN"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        return response
    
    return app
