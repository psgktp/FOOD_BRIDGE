import os
from flask import Flask
from app.config import Config
from app.extensions import db, login_manager
from app.models.user import User

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize Extensions
    db.init_app(app)
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
        
    # Register Blueprints
    from app.routes import (
        auth_bp, donor_bp, org_bp, volunteer_bp,
        finder_bp, admin_bp, main_bp, api_bp
    )
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(donor_bp)
    app.register_blueprint(org_bp)
    app.register_blueprint(volunteer_bp)
    app.register_blueprint(finder_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)
    
    # Context Processor for Templates
    @app.context_processor
    def inject_globals():
        return {
            'app_name': 'FoodBridge',
            'version': '2.0.0'
        }
        
    return app
