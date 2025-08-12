# routes.py
from .auth_routes import register_auth_routes
from .main_routes import register_main_routes
from .dimension_routes import register_dimension_routes
from .transaction_routes import register_transaction_routes
from .custody_routes import register_custody_routes


def register_routes(app):
    register_auth_routes(app)
    register_main_routes(app)
    register_dimension_routes(app)
    register_transaction_routes(app)
    register_custody_routes(app)
