"""
Databricks PS Risk Assessment Tool - Flask Application

Main application entry point for the backend API server.
"""

from flask import Flask, jsonify
from flask_cors import CORS
from datetime import datetime

from backend.config import get_config
from backend.routes.engagements import engagements_bp
from backend.routes.metrics import metrics_bp
from backend.routes.import_data import import_bp
from backend.routes.databricks import databricks_bp
from backend.routes.feedback import feedback_bp
from backend.services.data_store import get_data_store


def create_app():
    """
    Create and configure the Flask application.
    """
    app = Flask(__name__)
    
    # Load configuration
    config = get_config()
    app.config['DEBUG'] = config.flask_debug
    app.config['ENV'] = config.flask_env
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    
    # Enable CORS for frontend
    CORS(app, resources={
        r"/api/*": {
            "origins": [
                f"http://localhost:{config.frontend_port}",
                f"http://127.0.0.1:{config.frontend_port}",
                f"http://localhost:{config.dashboard_port}",
            ],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"],
        }
    })
    
    # Register blueprints
    app.register_blueprint(engagements_bp, url_prefix='/api/engagements')
    app.register_blueprint(metrics_bp, url_prefix='/api/metrics')
    app.register_blueprint(import_bp, url_prefix='/api/import')
    app.register_blueprint(databricks_bp, url_prefix='/api/databricks')
    app.register_blueprint(feedback_bp, url_prefix='/api/feedback')
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """API health check endpoint."""
        store = get_data_store()
        
        return jsonify({
            "status": "healthy",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "databricks_configured": config.databricks.is_configured(),
            "demo_data_loaded": len(store.engagements) > 0,
            "engagement_count": len(store.engagements),
        })
    
    # Root endpoint
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint with API information."""
        return jsonify({
            "name": "Databricks PS Risk Assessment Tool API",
            "version": "1.0.0",
            "description": "Backend API for the PS Risk Assessment Tool",
            "endpoints": {
                "health": "/api/health",
                "engagements": "/api/engagements",
                "engagement_detail": "/api/engagements/{id}",
                "engagement_risk": "/api/engagements/{id}/risk",
                "engagement_explanation": "/api/engagements/{id}/explanation",
                "metrics": "/api/metrics",
                "metrics_summary": "/api/metrics/summary",
                "ai_status": "/api/metrics/ai-status",
            },
            "documentation": "See README.md for full API documentation",
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Not found",
            "message": "The requested resource was not found"
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }), 500
    
    return app


# Application instance
app = create_app()


if __name__ == '__main__':
    config = get_config()
    print(f"\n{'='*60}")
    print("Databricks PS Risk Assessment Tool - Backend API")
    print(f"{'='*60}")
    print(f"Starting server on http://localhost:{config.backend_port}")
    print(f"Environment: {config.flask_env}")
    print(f"Debug mode: {config.flask_debug}")
    print(f"{'='*60}\n")
    
    app.run(
        host='0.0.0.0',
        port=config.backend_port,
        debug=config.flask_debug
    )
