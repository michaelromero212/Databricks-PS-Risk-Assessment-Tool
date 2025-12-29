"""
User Feedback Routes
Handles user feedback and feature requests for PS AI Tooling implementation.
"""

from flask import Blueprint, jsonify, request
from datetime import datetime

feedback_bp = Blueprint('feedback', __name__)

# In-memory feedback store for POC
_feedback_store = []

@feedback_bp.route('/', methods=['POST'])
def submit_feedback():
    """Submit user feedback."""
    data = request.json or {}
    
    if not data.get('comment'):
        return jsonify({'error': 'Comment is required'}), 400
        
    feedback_entry = {
        'id': len(_feedback_store) + 1,
        'user_email': data.get('user_email', 'anonymous@databricks.com'),
        'rating': data.get('rating', 5),
        'comment': data.get('comment'),
        'category': data.get('category', 'General'),
        'submitted_at': datetime.now().isoformat()
    }
    
    _feedback_store.append(feedback_entry)
    
    # In a real app, this would be logged to Databricks/Delta or a feedback system
    print(f"FEEDBACK RECEIVED: {feedback_entry}")
    
    return jsonify({
        'success': True, 
        'message': 'Thank you for your feedback! This helps drive PS AI Tooling prioritization.',
        'feedback_id': feedback_entry['id']
    })

@feedback_bp.route('/summary', methods=['GET'])
def get_feedback_summary():
    """Get summarized feedback for program tracking."""
    if not _feedback_store:
        return jsonify({
            'count': 0,
            'avg_rating': 0,
            'recent': []
        })
        
    avg_rating = sum(f['rating'] for f in _feedback_store) / len(_feedback_store)
    
    return jsonify({
        'count': len(_feedback_store),
        'avg_rating': round(avg_rating, 1),
        'recent': sorted(_feedback_store, key=lambda x: x['submitted_at'], reverse=True)[:5]
    })
