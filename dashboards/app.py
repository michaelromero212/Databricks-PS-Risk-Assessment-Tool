"""
Databricks PS Risk Assessment Tool - Dash Dashboard Application

Interactive analytics dashboard built with Dash and Plotly.
"""

import os
import sys
from datetime import datetime, timedelta
import random

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import requests

from dashboards.layouts.risk_dashboard import create_dashboard_layout, create_metric_card
from dashboards.components.charts import (
    create_risk_distribution_pie,
    create_industry_bar,
    create_risk_trend_line,
    COLORS
)

# Backend API URL
API_URL = os.getenv('REACT_APP_API_URL', 'http://localhost:5001')

# Initialize Dash app
app = Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap'
    ],
    title='PS Risk Assessment Dashboard',
    suppress_callback_exceptions=True
)

# Set layout
app.layout = create_dashboard_layout()


def fetch_api(endpoint):
    """Fetch data from the backend API."""
    try:
        response = requests.get(f'{API_URL}/api{endpoint}', timeout=5)
        if response.ok:
            return response.json()
    except Exception as e:
        print(f"API error: {e}")
    return None


@callback(
    [
        Output('metrics-row', 'children'),
        Output('risk-distribution-chart', 'figure'),
        Output('industry-chart', 'figure'),
        Output('trend-chart', 'figure'),
        Output('engagement-table', 'children'),
        Output('ai-status-indicator', 'children'),
        Output('ai-metadata', 'children')
    ],
    Input('refresh-interval', 'n_intervals')
)
def update_dashboard(n):
    """Update all dashboard components."""
    
    # Fetch data
    metrics = fetch_api('/metrics/summary')
    engagements_data = fetch_api('/engagements')
    ai_status = fetch_api('/metrics/ai-status')
    
    # Default values if API unavailable
    if not metrics:
        metrics = {
            'overview': {'total_engagements': 0, 'avg_risk_score': 0, 'ai_coverage': 0},
            'risk_distribution': {'high': 0, 'medium': 0, 'low': 0},
            'industries': {}
        }
    
    if not engagements_data:
        engagements_data = {'engagements': []}
    
    engagements = engagements_data.get('engagements', [])
    
    # =========================================================================
    # Metrics Row
    # =========================================================================
    metrics_cards = [
        create_metric_card(
            'Active Engagements',
            metrics['overview'].get('total_engagements', 0),
            color='#ff3621'
        ),
        create_metric_card(
            'High Risk',
            metrics['risk_distribution'].get('high', 0),
            color='#e64545'
        ),
        create_metric_card(
            'Medium Risk',
            metrics['risk_distribution'].get('medium', 0),
            color='#e6a23c'
        ),
        create_metric_card(
            'Low Risk',
            metrics['risk_distribution'].get('low', 0),
            color='#2e9e5e'
        ),
        create_metric_card(
            'Avg Risk Score',
            f"{metrics['overview'].get('avg_risk_score', 0):.1f}",
            subtitle='out of 100'
        ),
        create_metric_card(
            'AI Coverage',
            f"{metrics['overview'].get('ai_coverage', 0):.0f}%",
            subtitle='explanations generated'
        )
    ]
    
    # =========================================================================
    # Risk Distribution Chart
    # =========================================================================
    risk_dist = metrics['risk_distribution']
    risk_chart = create_risk_distribution_pie(
        risk_dist.get('high', 0),
        risk_dist.get('medium', 0),
        risk_dist.get('low', 0)
    )
    
    # =========================================================================
    # Industry Chart
    # =========================================================================
    industries = metrics.get('industries', {})
    if industries:
        industry_names = list(industries.keys())
        industry_counts = list(industries.values())
    else:
        industry_names = ['No Data']
        industry_counts = [0]
    
    industry_chart = create_industry_bar(industry_names, industry_counts)
    
    # =========================================================================
    # Trend Chart (Simulated historical data)
    # =========================================================================
    # Generate simulated historical trend
    dates = [(datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d') for i in range(13, -1, -1)]
    
    # Use current avg score and create a trend
    current_avg = metrics['overview'].get('avg_risk_score', 50)
    scores = []
    levels = []
    
    for i, d in enumerate(dates):
        # Add some variation
        variation = (random.random() - 0.5) * 20
        score = max(0, min(100, current_avg + variation - (13 - i) * 0.5))
        scores.append(score)
        
        if score <= 35:
            levels.append('Low')
        elif score <= 65:
            levels.append('Medium')
        else:
            levels.append('High')
    
    trend_chart = create_risk_trend_line(dates, scores, levels)
    
    # =========================================================================
    # Engagement Table
    # =========================================================================
    table_header = html.Thead(html.Tr([
        html.Th('Customer', style={'color': '#a0a0b8', 'fontSize': '0.75rem', 'textTransform': 'uppercase', 'padding': '0.75rem 1rem'}),
        html.Th('Industry', style={'color': '#a0a0b8', 'fontSize': '0.75rem', 'textTransform': 'uppercase', 'padding': '0.75rem 1rem'}),
        html.Th('Risk Level', style={'color': '#a0a0b8', 'fontSize': '0.75rem', 'textTransform': 'uppercase', 'padding': '0.75rem 1rem'}),
        html.Th('Score', style={'color': '#a0a0b8', 'fontSize': '0.75rem', 'textTransform': 'uppercase', 'padding': '0.75rem 1rem'}),
        html.Th('Trend', style={'color': '#a0a0b8', 'fontSize': '0.75rem', 'textTransform': 'uppercase', 'padding': '0.75rem 1rem'}),
        html.Th('SA Assigned', style={'color': '#a0a0b8', 'fontSize': '0.75rem', 'textTransform': 'uppercase', 'padding': '0.75rem 1rem'})
    ]), style={'background': '#252542'})
    
    def get_risk_badge_style(level):
        colors = {
            'High': {'bg': 'rgba(230, 69, 69, 0.15)', 'color': '#e64545', 'border': 'rgba(230, 69, 69, 0.4)'},
            'Medium': {'bg': 'rgba(230, 162, 60, 0.15)', 'color': '#e6a23c', 'border': 'rgba(230, 162, 60, 0.4)'},
            'Low': {'bg': 'rgba(46, 158, 94, 0.15)', 'color': '#2e9e5e', 'border': 'rgba(46, 158, 94, 0.4)'}
        }
        c = colors.get(level, colors['Low'])
        return {
            'background': c['bg'],
            'color': c['color'],
            'border': f"1px solid {c['border']}",
            'padding': '0.25rem 0.75rem',
            'borderRadius': '9999px',
            'fontSize': '0.75rem',
            'fontWeight': '600',
            'textTransform': 'uppercase',
            'display': 'inline-block'
        }
    
    def get_trend_indicator(direction):
        icons = {'improving': '↓', 'stable': '→', 'degrading': '↑'}
        colors = {'improving': '#2e9e5e', 'stable': '#6b6b84', 'degrading': '#e64545'}
        d = direction.lower() if direction else 'stable'
        return html.Span([
            html.Span(icons.get(d, '→'), style={'marginRight': '0.25rem'}),
            d.capitalize()
        ], style={'color': colors.get(d, '#6b6b84'), 'fontSize': '0.875rem'})
    
    table_rows = []
    for eng in engagements:
        table_rows.append(html.Tr([
            html.Td(eng.get('customer_name', 'N/A'), style={'padding': '0.75rem 1rem', 'color': '#ffffff', 'fontWeight': '500'}),
            html.Td(eng.get('industry', 'N/A'), style={'padding': '0.75rem 1rem', 'color': '#a0a0b8'}),
            html.Td(
                html.Span(eng.get('risk_level', 'N/A'), style=get_risk_badge_style(eng.get('risk_level', 'Low'))),
                style={'padding': '0.75rem 1rem'}
            ),
            html.Td(f"{eng.get('risk_score', 0):.0f}", style={'padding': '0.75rem 1rem', 'color': '#ffffff'}),
            html.Td(get_trend_indicator(eng.get('trend_direction')), style={'padding': '0.75rem 1rem'}),
            html.Td(eng.get('sa_assigned', 'N/A'), style={'padding': '0.75rem 1rem', 'color': '#a0a0b8'})
        ], style={'borderBottom': '1px solid rgba(255, 255, 255, 0.08)'}))
    
    if not table_rows:
        table_rows = [html.Tr(html.Td('No engagements found', colSpan=6, style={
            'padding': '2rem', 'textAlign': 'center', 'color': '#6b6b84'
        }))]
    
    engagement_table = html.Table([table_header, html.Tbody(table_rows)], style={
        'width': '100%',
        'borderCollapse': 'collapse'
    })
    
    # =========================================================================
    # AI Status
    # =========================================================================
    if ai_status:
        status_dot_style = {
            'width': '8px',
            'height': '8px',
            'borderRadius': '50%',
            'background': '#2e9e5e',
            'marginRight': '0.5rem',
            'display': 'inline-block'
        }
        
        if not ai_status.get('model_loaded', False):
            status_dot_style['background'] = '#e6a23c'
            status_text = 'Using Fallback'
        else:
            status_text = 'Model Ready'
        
        ai_status_indicator = html.Span([
            html.Span(style=status_dot_style),
            html.Span(status_text, style={'fontSize': '0.875rem', 'color': '#a0a0b8'})
        ], style={'display': 'flex', 'alignItems': 'center'})
        
        ai_metadata = [
            html.Div([
                html.Div('Model Name', style={'fontSize': '0.75rem', 'color': '#6b6b84', 'textTransform': 'uppercase', 'letterSpacing': '0.05em'}),
                html.Div(ai_status.get('model_name', 'N/A'), style={'fontSize': '0.875rem', 'color': '#ffffff', 'marginTop': '0.25rem'})
            ]),
            html.Div([
                html.Div('Provider', style={'fontSize': '0.75rem', 'color': '#6b6b84', 'textTransform': 'uppercase', 'letterSpacing': '0.05em'}),
                html.Div(ai_status.get('model_provider', 'N/A'), style={'fontSize': '0.875rem', 'color': '#ffffff', 'marginTop': '0.25rem'})
            ]),
            html.Div([
                html.Div('Purpose', style={'fontSize': '0.75rem', 'color': '#6b6b84', 'textTransform': 'uppercase', 'letterSpacing': '0.05em'}),
                html.Div(ai_status.get('model_purpose', 'N/A'), style={'fontSize': '0.875rem', 'color': '#ffffff', 'marginTop': '0.25rem'})
            ]),
            html.Div([
                html.Div('Cache Size', style={'fontSize': '0.75rem', 'color': '#6b6b84', 'textTransform': 'uppercase', 'letterSpacing': '0.05em'}),
                html.Div(str(ai_status.get('cache_size', 0)), style={'fontSize': '0.875rem', 'color': '#ffffff', 'marginTop': '0.25rem'})
            ])
        ]
    else:
        ai_status_indicator = html.Span('Status Unknown', style={'color': '#6b6b84', 'fontSize': '0.875rem'})
        ai_metadata = [html.Div('Unable to fetch AI status', style={'color': '#6b6b84'})]
    
    return (
        metrics_cards,
        risk_chart,
        industry_chart,
        trend_chart,
        engagement_table,
        ai_status_indicator,
        ai_metadata
    )


# Server for deployment
server = app.server

if __name__ == '__main__':
    port = int(os.getenv('DASHBOARD_PORT', 8050))
    print(f"\n{'='*60}")
    print("Databricks PS Risk Assessment Tool - Dash Dashboard")
    print(f"{'='*60}")
    print(f"Starting server on http://localhost:{port}")
    print(f"Backend API: {API_URL}")
    print(f"{'='*60}\n")
    
    app.run(
        debug=True,
        host='0.0.0.0',
        port=port
    )
