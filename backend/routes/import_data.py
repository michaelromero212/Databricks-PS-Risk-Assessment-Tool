"""
Data Import Routes

Handles CSV file uploads for engagement data and provides template downloads.
"""

import csv
import io
from datetime import datetime, timedelta
from flask import Blueprint, jsonify, request, Response
from backend.services.data_store import get_data_store
from backend.services.risk_engine import get_risk_engine
from backend.models import (
    Engagement, PlatformSignal, Industry, ScopeSize
)

import_bp = Blueprint('import_data', __name__)

# Sample engagement template
ENGAGEMENT_TEMPLATE = """customer_name,industry,start_date,target_completion_date,scope_size,sa_assigned,sa_confidence_score
Global Retail Corp,Retail,2025-01-15,2025-04-15,large,John Smith,3
Healthcare Analytics Inc,Healthcare,2025-02-01,2025-05-01,medium,Jane Doe,4
FinTech Solutions,Financial Services,2025-01-20,2025-03-20,small,Mike Wilson,5
Manufacturing Plus,Manufacturing,2025-02-10,2025-06-10,large,Sarah Chen,2
Energy Systems Co,Energy,2025-01-25,2025-04-25,medium,David Kim,4
Tech Startup Alpha,Technology,2025-02-15,2025-05-15,small,Emily Rodriguez,3
"""

# Sample signals template
SIGNALS_TEMPLATE = """engagement_id,signal_date,job_success_count,job_failure_count,avg_job_duration_seconds,notebook_execution_count,sql_query_count
eng-import-001,2025-01-16,15,2,120,10,45
eng-import-001,2025-01-17,18,1,115,12,52
eng-import-001,2025-01-18,12,3,130,8,38
eng-import-002,2025-02-02,20,0,95,15,60
eng-import-002,2025-02-03,22,1,100,18,72
"""


@import_bp.route('/templates/engagements', methods=['GET'])
def download_engagement_template():
    """Download sample engagement CSV template."""
    return Response(
        ENGAGEMENT_TEMPLATE,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=sample_engagements.csv'}
    )


@import_bp.route('/templates/signals', methods=['GET'])
def download_signals_template():
    """Download sample signals CSV template."""
    return Response(
        SIGNALS_TEMPLATE,
        mimetype='text/csv',
        headers={'Content-Disposition': 'attachment; filename=sample_signals.csv'}
    )


@import_bp.route('/engagements', methods=['POST'])
def import_engagements():
    """
    Import engagements from CSV file.
    
    Expected CSV columns:
    - customer_name (required)
    - industry (required): Technology, Healthcare, Financial Services, Retail, Manufacturing, Energy
    - start_date (required): YYYY-MM-DD
    - target_completion_date (required): YYYY-MM-DD
    - scope_size (required): small, medium, large
    - sa_assigned (required)
    - sa_confidence_score (required): 1-5
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file provided'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file.filename.endswith('.csv'):
        return jsonify({'error': 'File must be a CSV'}), 400
    
    try:
        # Read CSV content
        content = file.read().decode('utf-8')
        reader = csv.DictReader(io.StringIO(content))
        
        store = get_data_store()
        risk_engine = get_risk_engine()
        imported = []
        errors = []
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
            try:
                # Parse industry
                industry_map = {
                    'technology': Industry.TECHNOLOGY,
                    'healthcare': Industry.HEALTHCARE,
                    'financial services': Industry.FINANCIAL_SERVICES,
                    'retail': Industry.RETAIL,
                    'manufacturing': Industry.MANUFACTURING,
                    'energy': Industry.ENERGY,
                }
                industry = industry_map.get(row['industry'].lower().strip())
                if not industry:
                    errors.append(f"Row {row_num}: Invalid industry '{row['industry']}'")
                    continue
                
                # Parse scope size
                scope_map = {
                    'small': ScopeSize.SMALL,
                    'medium': ScopeSize.MEDIUM,
                    'large': ScopeSize.LARGE,
                }
                scope = scope_map.get(row['scope_size'].lower().strip())
                if not scope:
                    errors.append(f"Row {row_num}: Invalid scope_size '{row['scope_size']}'")
                    continue
                
                # Parse dates
                try:
                    start_date = datetime.strptime(row['start_date'].strip(), '%Y-%m-%d')
                    target_date = datetime.strptime(row['target_completion_date'].strip(), '%Y-%m-%d')
                except ValueError as e:
                    errors.append(f"Row {row_num}: Invalid date format - {str(e)}")
                    continue
                
                # Parse confidence score
                try:
                    confidence = int(row['sa_confidence_score'].strip())
                    if confidence < 1 or confidence > 5:
                        errors.append(f"Row {row_num}: Confidence score must be 1-5")
                        continue
                except ValueError:
                    errors.append(f"Row {row_num}: Invalid confidence score")
                    continue
                
                # Generate unique ID
                eng_id = f"eng-import-{len(store.engagements) + len(imported) + 1:03d}"
                
                # Create engagement
                engagement = Engagement(
                    engagement_id=eng_id,
                    customer_name=row['customer_name'].strip(),
                    industry=industry,
                    start_date=start_date,
                    target_completion_date=target_date,
                    scope_size=scope,
                    sa_assigned=row['sa_assigned'].strip(),
                    sa_confidence_score=confidence,
                )
                
                # Add to store
                store.add_engagement(engagement)
                
                # Generate simulated signals for the engagement
                _generate_sample_signals(store, eng_id, start_date)
                
                # Compute risk score - get signals we just generated
                signals = store.get_engagement_signals(eng_id)
                previous_scores = store.get_risk_history(eng_id)
                risk_score = risk_engine.compute_risk_score(engagement, signals, previous_scores)
                if risk_score:
                    store.add_risk_score(risk_score)
                
                # Generate AI explanation
                from backend.services.ai_explainer import get_ai_explainer
                explainer = get_ai_explainer()
                if risk_score:
                    explanation = explainer.generate_explanation(engagement, risk_score)
                    if explanation:
                        store.add_explanation(explanation)
                
                imported.append({
                    'engagement_id': eng_id,
                    'customer_name': engagement.customer_name,
                    'risk_score': risk_score.risk_score if risk_score else None,
                    'risk_level': risk_score.risk_level.value if risk_score else None,
                })
                
            except KeyError as e:
                errors.append(f"Row {row_num}: Missing required column {str(e)}")
            except Exception as e:
                errors.append(f"Row {row_num}: {str(e)}")
        
        return jsonify({
            'success': True,
            'imported_count': len(imported),
            'imported': imported,
            'errors': errors,
            'total_engagements': len(store.engagements)
        })
        
    except Exception as e:
        return jsonify({'error': f'Failed to parse CSV: {str(e)}'}), 500


def _generate_sample_signals(store, engagement_id: str, start_date):
    """Generate sample platform signals for a new engagement."""
    import random
    from datetime import date as date_type
    
    # Convert start_date to date if it's a datetime
    if isinstance(start_date, datetime):
        start_date_normalized = start_date.date()
    elif isinstance(start_date, date_type):
        start_date_normalized = start_date
    else:
        start_date_normalized = datetime.now().date() - timedelta(days=14)
    
    # Generate signals for the past 14 days
    for i in range(14):
        signal_datetime = datetime.now() - timedelta(days=13-i)
        signal_date = signal_datetime.date()
        
        # Skip if signal date is before engagement start
        if signal_date < start_date_normalized:
            continue
            
        signal = PlatformSignal(
            engagement_id=engagement_id,
            signal_date=signal_date,
            job_success_count=random.randint(8, 25),
            job_failure_count=random.randint(0, 5),
            avg_job_duration_seconds=random.uniform(80, 180),
            notebook_execution_count=random.randint(5, 20),
            sql_query_count=random.randint(20, 100),
            last_activity_timestamp=signal_datetime.replace(hour=15, minute=0, second=0),
        )
        store.add_signal(signal)


@import_bp.route('/status', methods=['GET'])
def import_status():
    """Get current data store status."""
    store = get_data_store()
    return jsonify({
        'total_engagements': len(store.engagements),
        'total_signals': sum(len(signals) for signals in store.signals.values()),
        'total_risk_scores': len(store.risk_scores),
        'total_explanations': len(store.explanations),
    })
