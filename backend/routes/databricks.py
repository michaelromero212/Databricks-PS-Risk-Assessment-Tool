"""
Databricks Workspace Routes

Exposes endpoints for Databricks workspace information and Unity Catalog browsing.
"""

from flask import Blueprint, jsonify, request
from backend.services.databricks_client import get_databricks_client

databricks_bp = Blueprint('databricks', __name__)

@databricks_bp.route('/info', methods=['GET'])
def get_workspace_info():
    """Get information about the connected Databricks workspace."""
    client = get_databricks_client()
    info = client.get_workspace_info()
    return jsonify({
        'host': info.host,
        'connected': info.connected,
        'user_email': info.user_email,
        'workspace_id': info.workspace_id,
        'error': info.error
    })

@databricks_bp.route('/catalogs', methods=['GET'])
def list_catalogs():
    """List all Unity Catalogs."""
    client = get_databricks_client()
    catalogs = client.list_catalogs()
    return jsonify([
        {
            'name': cat.name,
            'comment': cat.comment,
            'owner': cat.owner,
            'schema_count': cat.schema_count
        } for cat in catalogs
    ])

@databricks_bp.route('/catalogs/<catalog_name>/schemas', methods=['GET'])
def list_schemas(catalog_name):
    """List schemas in a catalog."""
    client = get_databricks_client()
    schemas = client.list_schemas(catalog_name)
    return jsonify([
        {
            'name': schema.name,
            'catalog_name': schema.catalog_name,
            'comment': schema.comment,
            'table_count': schema.table_count
        } for schema in schemas
    ])

@databricks_bp.route('/connect', methods=['POST'])
def connect_workspace():
    """Establish connection to Databricks."""
    data = request.json or {}
    host = data.get('host')
    token = data.get('token')
    
    client = get_databricks_client()
    if host and token:
        # Override current config if provided
        client.host = host
        client.token = token
    
    info = client.connect()
    return jsonify({
        'host': info.host,
        'connected': info.connected,
        'user_email': info.user_email,
        'workspace_id': info.workspace_id,
        'error': info.error
    })
