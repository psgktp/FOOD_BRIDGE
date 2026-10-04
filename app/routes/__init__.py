from app.routes.auth_routes import auth_bp
from app.routes.donor_routes import donor_bp
from app.routes.org_routes import org_bp
from app.routes.volunteer_routes import volunteer_bp
from app.routes.finder_routes import finder_bp
from app.routes.admin_routes import admin_bp
from app.routes.main_routes import main_bp
from app.routes.api_routes import api_bp

__all__ = [
    'auth_bp',
    'donor_bp',
    'org_bp',
    'volunteer_bp',
    'finder_bp',
    'admin_bp',
    'main_bp',
    'api_bp'
]
